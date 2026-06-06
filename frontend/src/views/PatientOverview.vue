<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">
        <el-button @click="goBack" style="margin-right: 10px;">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        患者随访概览
      </div>
      <el-button
        type="primary"
        @click="handleAddPlan"
        :disabled="userStore.isAuditor()"
      >
        <el-icon><Plus /></el-icon>
        新建回访计划
      </el-button>
    </div>

    <div v-loading="loading" class="overview-content">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="info-card">
            <div class="patient-info">
              <div class="info-item">
                <span class="label">患者编号：</span>
                <span class="value">{{ overview.patient_id || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">患者姓名：</span>
                <span class="value">{{ overview.patient_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">随访总次数：</span>
                <span class="value">{{ overview.total_records || 0 }}</span>
              </div>
              <div class="info-item">
                <span class="label">最新评分：</span>
                <span class="value">
                  <el-tag v-if="overview.latest_score !== null" :type="getScoreTagType(overview.latest_score)">
                    {{ overview.latest_score }}
                  </el-tag>
                  <span v-else>-</span>
                </span>
              </div>
              <div class="info-item">
                <span class="label">最近随访日期：</span>
                <span class="value">{{ overview.latest_followup_date ? formatDate(overview.latest_followup_date) : '-' }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>历史评分趋势</span>
                <el-button type="text" size="small" @click="viewScoreDetail">
                  查看明细
                </el-button>
              </div>
            </template>
            <v-chart v-if="overview.score_trend && overview.score_trend.length > 0" :option="trendChartOption" style="height: 300px;" />
            <el-empty v-else description="暂无评分数据" />
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>最近随访记录</span>
              </div>
            </template>
            <el-table :data="overview.recent_records || []" size="small" stripe>
              <el-table-column prop="followup_date" label="随访日期" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.followup_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="score" label="评分" width="80">
                <template #default="{ row }">
                  <el-tag :type="getScoreTagType(row.score)" size="small">
                    {{ row.score }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="batch_id" label="批次号" show-overflow-tooltip />
            </el-table>
            <div v-if="!overview.recent_records || overview.recent_records.length === 0" style="padding: 20px;">
              <el-empty description="暂无随访记录" :image-size="80" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>待处理回访计划</span>
                <el-badge v-if="overview.pending_plans && overview.pending_plans.length > 0" :value="overview.pending_plans.length" class="badge" />
              </div>
            </template>
            <el-table :data="overview.pending_plans || []" size="small" stripe>
              <el-table-column prop="plan_date" label="计划日期" width="150">
                <template #default="{ row }">
                  {{ formatDateTime(row.plan_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" v-if="!userStore.isAuditor()">
                <template #default="{ row }">
                  <el-button size="small" type="success" @click="markPlanComplete(row)">
                    完成
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="!overview.pending_plans || overview.pending_plans.length === 0" style="padding: 20px;">
              <el-empty description="暂无待处理计划" :image-size="80" />
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>未读异常提醒</span>
                <el-badge v-if="overview.unread_alerts && overview.unread_alerts.length > 0" :value="overview.unread_alerts.length" type="danger" class="badge" />
              </div>
            </template>
            <el-table :data="overview.unread_alerts || []" size="small" stripe>
              <el-table-column prop="alert_type" label="类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.alert_type.includes('下降') ? 'danger' : 'warning'" size="small">
                    {{ row.alert_type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息" show-overflow-tooltip />
              <el-table-column label="操作" width="90">
                <template #default="{ row }">
                  <el-button size="small" type="primary" @click="markAlertRead(row)">
                    标记已读
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="!overview.unread_alerts || overview.unread_alerts.length === 0" style="padding: 20px;">
              <el-empty description="暂无未读提醒" :image-size="80" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="scoreDetailVisible" title="评分变化明细" width="700px">
      <div v-if="scoreChanges.length > 0">
        <p style="margin-bottom: 15px;">
          患者: <strong>{{ scoreChanges[0].patient_name || scoreChanges[0].patient_id }}</strong>
        </p>
        <el-table :data="scoreChanges" border>
          <el-table-column prop="followup_date" label="随访日期" width="150">
            <template #default="{ row }">
              {{ formatDate(row.followup_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="score" label="当前评分" width="100" />
          <el-table-column prop="previous_score" label="上次评分" width="100" />
          <el-table-column prop="score_change" label="变化值" width="100">
            <template #default="{ row }">
              <span v-if="row.score_change !== null" :class="row.score_change >= 0 ? 'text-green' : 'text-red'">
                {{ row.score_change >= 0 ? '+' : '' }}{{ row.score_change }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
        <v-chart :option="detailChartOption" style="height: 250px; margin-top: 20px;" />
      </div>
      <div v-else>
        <el-empty description="暂无评分变化数据" />
      </div>
    </el-dialog>

    <el-dialog v-model="planDialogVisible" title="新建回访计划" width="500px">
      <el-form :model="planForm" :rules="planRules" ref="planFormRef" label-width="100px">
        <el-form-item label="患者编号" prop="patient_id">
          <el-input v-model="planForm.patient_id" disabled />
        </el-form-item>
        <el-form-item label="患者姓名">
          <el-input v-model="planForm.patient_name" :disabled="!!overview.patient_name" />
        </el-form-item>
        <el-form-item label="计划日期" prop="plan_date">
          <el-date-picker
            v-model="planForm.plan_date"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="planForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitPlan" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { getPatientOverview } from '@/api/overview'
import { getPatientScoreChanges } from '@/api/records'
import { createPlan, updatePlan } from '@/api/plans'
import { markAlertRead as markAlertReadApi } from '@/api/audit'
import dayjs from 'dayjs'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent])

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const overview = ref({})
const trendChartOption = ref({})
const scoreDetailVisible = ref(false)
const scoreChanges = ref([])
const detailChartOption = ref({})
const planDialogVisible = ref(false)
const planFormRef = ref(null)
const submitting = ref(false)

const planForm = reactive({
  patient_id: '',
  patient_name: '',
  plan_date: null,
  description: '',
  status: 'pending'
})

const planRules = {
  patient_id: [{ required: true, message: '请输入患者编号', trigger: 'blur' }],
  plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }]
}

const patientId = computed(() => route.params.patientId)

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')
const formatDateTime = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const getScoreTagType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

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

const fetchOverview = async () => {
  loading.value = true
  try {
    overview.value = await getPatientOverview(patientId.value)
    updateTrendChart()
  } catch (e) {
    console.error(e)
    ElMessage.error('获取患者概览失败')
  } finally {
    loading.value = false
  }
}

const updateTrendChart = () => {
  if (!overview.value.score_trend || overview.value.score_trend.length === 0) return

  trendChartOption.value = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: overview.value.score_trend.map(r => formatDate(r.followup_date))
    },
    yAxis: { type: 'value', min: 0, max: 100 },
    series: [{
      name: '评分',
      type: 'line',
      data: overview.value.score_trend.map(r => r.score),
      smooth: true,
      markPoint: {
        data: [
          { type: 'max', name: '最高分' },
          { type: 'min', name: '最低分' }
        ]
      }
    }]
  }
}

const viewScoreDetail = async () => {
  try {
    scoreChanges.value = await getPatientScoreChanges(patientId.value)
    scoreDetailVisible.value = true

    detailChartOption.value = {
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: scoreChanges.value.map(r => formatDate(r.followup_date))
      },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: [{
        name: '评分',
        type: 'line',
        data: scoreChanges.value.map(r => r.score),
        smooth: true,
        markPoint: {
          data: [
            { type: 'max', name: '最高分' },
            { type: 'min', name: '最低分' }
          ]
        }
      }]
    }
  } catch (e) {
    console.error(e)
  }
}

const handleAddPlan = () => {
  Object.assign(planForm, {
    patient_id: patientId.value,
    patient_name: overview.value.patient_name || '',
    plan_date: null,
    description: '',
    status: 'pending'
  })
  planDialogVisible.value = true
}

const handleSubmitPlan = async () => {
  if (!planFormRef.value) return
  await planFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await createPlan(planForm)
        ElMessage.success('创建成功')
        planDialogVisible.value = false
        fetchOverview()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const markPlanComplete = async (row) => {
  try {
    await updatePlan(row.id, { status: 'completed' })
    ElMessage.success('已标记为完成')
    fetchOverview()
  } catch (e) {
    console.error(e)
  }
}

const markAlertRead = async (row) => {
  try {
    await markAlertReadApi(row.id)
    ElMessage.success('已标记为已读')
    fetchOverview()
  } catch (e) {
    console.error(e)
  }
}

const goBack = () => {
  router.back()
}

onMounted(fetchOverview)
</script>

<style scoped>
.overview-content {
  padding: 0;
}

.info-card {
  margin-bottom: 0;
}

.patient-info {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  color: #909399;
  margin-right: 8px;
}

.info-item .value {
  font-weight: 500;
}

.chart-card,
.section-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  margin-left: 10px;
}

.text-green {
  color: #67c23a;
}

.text-red {
  color: #f56c6c;
}
</style>
