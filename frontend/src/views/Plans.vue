<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">回访计划</div>
      <el-button type="primary" @click="handleAdd" :disabled="userStore.isAuditor()">
        <el-icon><Plus /></el-icon>
        新建计划
      </el-button>
    </div>

    <el-card>
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="患者编号">
          <el-input v-model="searchForm.patient_id" placeholder="请输入患者编号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待回访" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchPlans">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="plans" stripe v-loading="loading">
        <el-table-column prop="patient_id" label="患者编号" width="120" />
        <el-table-column prop="patient_name" label="姓名" width="120" />
        <el-table-column prop="plan_date" label="计划日期" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.plan_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" v-if="!userStore.isAuditor()">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToOverview(row)">
              患者概览
            </el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="success" @click="markComplete(row)" v-if="row.status === 'pending'">
              完成
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)" v-if="userStore.isAdmin()">
              删除
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" v-else>
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToOverview(row)">
              患者概览
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑计划' : '新建计划'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="患者编号" prop="patient_id">
          <el-input v-model="form.patient_id" />
        </el-form-item>
        <el-form-item label="患者姓名">
          <el-input v-model="form.patient_name" />
        </el-form-item>
        <el-form-item label="计划日期" prop="plan_date">
          <el-date-picker
            v-model="form.plan_date"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待回访" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { getPlans, createPlan, updatePlan, deletePlan } from '@/api/plans'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const plans = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentId = ref(null)

const searchForm = ref({
  patient_id: '',
  status: ''
})

const form = reactive({
  patient_id: '',
  patient_name: '',
  plan_date: null,
  description: '',
  status: 'pending'
})

const rules = {
  patient_id: [{ required: true, message: '请输入患者编号', trigger: 'blur' }],
  plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }]
}

const formatDateTime = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const getStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'completed': 'success',
    'cancelled': 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'pending': '待回访',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return texts[status] || status
}

const fetchPlans = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.value.patient_id) {
      params.patient_id = searchForm.value.patient_id
    }
    if (searchForm.value.status) {
      params.status = searchForm.value.status
    }
    plans.value = await getPlans(params)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const goToOverview = (row) => {
  router.push(`/patient/${row.patient_id}/overview`)
}

const resetSearch = () => {
  searchForm.value = {
    patient_id: '',
    status: ''
  }
  fetchPlans()
}

const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  Object.assign(form, {
    patient_id: '',
    patient_name: '',
    plan_date: null,
    description: '',
    status: 'pending'
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, {
    patient_id: row.patient_id,
    patient_name: row.patient_name,
    plan_date: new Date(row.plan_date),
    description: row.description,
    status: row.status
  })
  dialogVisible.value = true
}

const markComplete = async (row) => {
  try {
    await updatePlan(row.id, { status: 'completed' })
    ElMessage.success('已标记为完成')
    fetchPlans()
  } catch (e) {
    console.error(e)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该计划吗？', '提示', {
      type: 'warning'
    })
    await deletePlan(row.id)
    ElMessage.success('删除成功')
    fetchPlans()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await updatePlan(currentId.value, form)
          ElMessage.success('更新成功')
        } else {
          await createPlan(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchPlans()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(fetchPlans)
</script>

<style scoped>
.search-form {
  margin-bottom: 20px;
}
</style>
