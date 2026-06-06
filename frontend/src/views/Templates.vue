<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">模板管理</div>
      <el-button type="primary" @click="handleAdd" :disabled="!userStore.isAdmin()">
        <el-icon><Plus /></el-icon>
        新建模板
      </el-button>
    </div>

    <el-card>
      <el-table :data="templates" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="模板名称" width="200" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="评分范围" width="150">
          <template #default="{ row }">
            {{ row.score_min }} - {{ row.score_max }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" v-if="userStore.isAdmin()">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑模板' : '新建模板'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="字段定义" prop="fields">
          <el-input
            v-model="form.fields"
            type="textarea"
            :rows="4"
            placeholder="JSON格式定义字段，例如：{\"血压\": \"string\", \"心率\": \"number\"}"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低评分" prop="score_min">
              <el-input-number v-model="form.score_min" :min="0" :max="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高评分" prop="score_max">
              <el-input-number v-model="form.score_max" :min="0" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { getTemplates, createTemplate, updateTemplate, deleteTemplate } from '@/api/templates'
import dayjs from 'dayjs'

const userStore = useUserStore()

const templates = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentId = ref(null)

const form = reactive({
  name: '',
  description: '',
  fields: '',
  score_min: 0,
  score_max: 100
})

const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  fields: [{ required: true, message: '请输入字段定义', trigger: 'blur' }]
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')

const fetchTemplates = async () => {
  loading.value = true
  try {
    templates.value = await getTemplates()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  Object.assign(form, {
    name: '',
    description: '',
    fields: '',
    score_min: 0,
    score_max: 100
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, {
    name: row.name,
    description: row.description,
    fields: row.fields,
    score_min: row.score_min,
    score_max: row.score_max
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
      type: 'warning'
    })
    await deleteTemplate(row.id)
    ElMessage.success('删除成功')
    fetchTemplates()
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
          await updateTemplate(currentId.value, form)
          ElMessage.success('更新成功')
        } else {
          await createTemplate(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchTemplates()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(fetchTemplates)
</script>
