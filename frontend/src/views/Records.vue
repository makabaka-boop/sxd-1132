<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">随访记录</div>
    </div>

    <el-card>
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="患者编号">
          <el-input v-model="searchForm.patient_id" placeholder="请输入患者编号" clearable />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchRecords">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="records" stripe v-loading="loading">
        <el-table-column prop="patient_id" label="患者编号" width="120" />
        <el-table-column prop="patient_name" label="姓名" width="120" />
        <el-table-column prop="followup_date" label="随访日期" width="150">
          <template #default="{ row }">
            {{ formatDate(row.followup_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="score" label="评分" width="100">
          <template #default="{ row }">
            <el-tag :type="getScoreTagType(row.score)">
              {{ row.score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="batch_id" label="批次号" width="220" show-overflow-tooltip />
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToOverview(row)">
              患者概览
            </el-button>
            <el-button size="small" @click="viewScoreTrend(row)">
              评分趋势
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="trendDialogVisible" title="评分变化趋势" width="700px">
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
        <v-chart :option="trendChartOption" style="height: 250px; margin-top: 20px;" />
      </div>
      <div v-else>
        <el-empty description="暂无评分变化数据" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getRecords, getPatientScoreChanges } from '@/api/records'
import dayjs from 'dayjs'

const router = useRouter()

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent])

const records = ref([])
const loading = ref(false)
const trendDialogVisible = ref(false)
const scoreChanges = ref([])
const trendChartOption = ref({})

const searchForm = ref({
  patient_id: '',
  dateRange: []
})

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')
const formatDateTime = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')

const getScoreTagType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.value.patient_id) {
      params.patient_id = searchForm.value.patient_id
    }
    if (searchForm.value.dateRange && searchForm.value.dateRange.length === 2) {
      params.start_date = dayjs(searchForm.value.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(searchForm.value.dateRange[1]).format('YYYY-MM-DD')
    }
    records.value = await getRecords(params)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.value = {
    patient_id: '',
    dateRange: []
  }
  fetchRecords()
}

const goToOverview = (row) => {
  router.push(`/patient/${row.patient_id}/overview`)
}

const viewScoreTrend = async (row) => {
  try {
    scoreChanges.value = await getPatientScoreChanges(row.patient_id)
    trendDialogVisible.value = true

    trendChartOption.value = {
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

onMounted(fetchRecords)
</script>

<style scoped>
.search-form {
  margin-bottom: 20px;
}

.text-green {
  color: #67c23a;
}

.text-red {
  color: #f56c6c;
}
</style>
