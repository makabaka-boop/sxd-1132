<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">审计日志</div>
    </div>

    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="处理日志" name="logs">
          <el-table :data="auditLogs" stripe v-loading="logsLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="操作人" width="150">
              <template #default="{ row }">
                {{ row.user?.full_name || row.user?.username || '-' }}
                <el-tag size="small" style="margin-left: 5px;">{{ getRoleText(row.user?.role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="action" label="操作" width="200" />
            <el-table-column prop="batch_id" label="批次号" width="220" show-overflow-tooltip />
            <el-table-column prop="details" label="详情" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="错误行查看" name="errors">
          <div style="margin-bottom: 15px;">
            <el-input
              v-model="batchIdSearch"
              placeholder="请输入批次号查询错误记录"
              style="width: 300px;"
              clearable
            >
              <template #append>
                <el-button @click="fetchErrors">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
          <el-table :data="errorRecords" stripe v-loading="errorsLoading">
            <el-table-column prop="row_number" label="行号" width="80" />
            <el-table-column prop="patient_id" label="患者编号" width="120" />
            <el-table-column prop="error_type" label="错误类型" width="120">
              <template #default="{ row }">
                <el-tag type="danger" size="small">{{ row.error_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
            <el-table-column prop="row_data" label="原始数据" show-overflow-tooltip>
              <template #default="{ row }">
                <el-popover placement="top-start" title="原始数据" :width="400" trigger="hover">
                  <template #reference>
                    <span style="cursor: pointer; color: #409EFF;">查看详情</span>
                  </template>
                  <pre style="white-space: pre-wrap; word-break: break-all;">{{ row.row_data }}</pre>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!errorsLoading && errorRecords.length === 0" description="请输入批次号查询" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAuditLogs, getBatchErrors } from '@/api/audit'
import dayjs from 'dayjs'

const activeTab = ref('logs')
const auditLogs = ref([])
const errorRecords = ref([])
const logsLoading = ref(false)
const errorsLoading = ref(false)
const batchIdSearch = ref('')

const formatDateTime = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')

const getRoleText = (role) => {
  const roles = {
    'admin': '管理员',
    'user': '普通用户',
    'auditor': '审计员'
  }
  return roles[role] || role
}

const fetchAuditLogs = async () => {
  logsLoading.value = true
  try {
    auditLogs.value = await getAuditLogs({ limit: 100 })
  } catch (e) {
    console.error(e)
  } finally {
    logsLoading.value = false
  }
}

const fetchErrors = async () => {
  if (!batchIdSearch.value) return
  errorsLoading.value = true
  try {
    errorRecords.value = await getBatchErrors(batchIdSearch.value)
  } catch (e) {
    console.error(e)
  } finally {
    errorsLoading.value = false
  }
}

onMounted(fetchAuditLogs)
</script>
