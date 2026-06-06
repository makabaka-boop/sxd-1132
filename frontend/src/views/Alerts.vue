<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">异常提醒</div>
      <el-radio-group v-model="filterType" @change="fetchAlerts">
        <el-radio-button label="unread">未读</el-radio-button>
        <el-radio-button label="all">全部</el-radio-button>
      </el-radio-group>
    </div>

    <el-card>
      <el-table :data="alerts" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="patient_id" label="患者编号" width="120" />
        <el-table-column prop="patient_name" label="姓名" width="120" />
        <el-table-column prop="alert_type" label="类型" width="140">
          <template #default="{ row }">
            <el-tag :type="row.alert_type.includes('下降') ? 'danger' : 'warning'" size="small">
              {{ row.alert_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'danger'" size="small">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="markRead(row)"
              v-if="!row.is_read"
            >
              标记已读
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAlerts, markAlertRead } from '@/api/audit'
import dayjs from 'dayjs'

const alerts = ref([])
const loading = ref(false)
const filterType = ref('unread')

const formatDateTime = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')

const fetchAlerts = async () => {
  loading.value = true
  try {
    const params = filterType.value === 'unread' ? { is_read: false } : { is_read: null }
    alerts.value = await getAlerts(params)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const markRead = async (row) => {
  try {
    await markAlertRead(row.id)
    ElMessage.success('已标记为已读')
    fetchAlerts()
  } catch (e) {
    console.error(e)
  }
}

onMounted(fetchAlerts)
</script>
