<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-blue">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalRecords }}</div>
              <div class="stat-label">随访记录总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-green">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalPatients }}</div>
              <div class="stat-label">患者人数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-orange">
              <el-icon :size="30"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingPlans }}</div>
              <div class="stat-label">待回访计划</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-red">
              <el-icon :size="30"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.unreadAlerts }}</div>
              <div class="stat-label">未读异常提醒</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>评分趋势</span>
          </template>
          <v-chart :option="scoreChartOption" style="height: 350px;" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近异常提醒</span>
          </template>
          <el-table :data="recentAlerts" stripe>
            <el-table-column prop="patient_id" label="患者编号" width="120" />
            <el-table-column prop="alert_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.alert_type.includes('下降') ? 'danger' : 'warning'" size="small">
                  {{ row.alert_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="消息" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getRecords } from '@/api/records'
import { getPlans } from '@/api/plans'
import { getAlerts } from '@/api/audit'
import dayjs from 'dayjs'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const stats = ref({
  totalRecords: 0,
  totalPatients: 0,
  pendingPlans: 0,
  unreadAlerts: 0
})

const recentAlerts = ref([])
const scoreChartOption = ref({})

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const fetchData = async () => {
  try {
    const [records, plans, alerts] = await Promise.all([
      getRecords({ limit: 1000 }),
      getPlans({ status: 'pending' }),
      getAlerts({ is_read: false })
    ])

    stats.value.totalRecords = records.length
    const patientIds = new Set(records.map(r => r.patient_id))
    stats.value.totalPatients = patientIds.size
    stats.value.pendingPlans = plans.length
    stats.value.unreadAlerts = alerts.length

    recentAlerts.value = alerts.slice(0, 5)

    const dateMap = {}
    records.forEach(r => {
      const date = dayjs(r.followup_date).format('YYYY-MM-DD')
      if (!dateMap[date]) {
        dateMap[date] = []
      }
      dateMap[date].push(r.score)
    })

    const dates = Object.keys(dateMap).sort()
    const avgScores = dates.map(d => {
      const scores = dateMap[d]
      return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
    })

    scoreChartOption.value = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['平均评分'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: [{
        name: '平均评分',
        type: 'line',
        data: avgScores,
        smooth: true,
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#409EFF' }
      }]
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(fetchData)
</script>

<style scoped>
.stat-card {
  cursor: pointer;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 15px;
}

.icon-blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.icon-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
.icon-orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.icon-red { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-info .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
