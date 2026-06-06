<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">批量导入随访记录</div>
    </div>

    <el-card>
      <el-form :model="form" label-width="100px">
        <el-form-item label="选择模板">
          <el-select v-model="form.template_id" placeholder="请选择随访模板" style="width: 300px">
            <el-option
              v-for="t in templates"
              :key="t.id"
              :label="t.name"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".csv,.xlsx,.xls"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 CSV、Excel 格式，文件需包含 patient_id、followup_date、score 列
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleUpload" :loading="uploading" :disabled="!canUpload">
            开始导入
          </el-button>
          <el-button @click="downloadTemplate">下载示例模板</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="uploadResult" style="margin-top: 20px;">
      <template #header>
        <div class="result-header">
          <span>导入结果</span>
          <el-tag type="info">批次号: {{ uploadResult.batch_id }}</el-tag>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="总行数" :value="uploadResult.total_rows" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="成功" :value="uploadResult.success_count">
            <template #suffix><el-icon class="success-icon"><CircleCheck /></el-icon></template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="失败" :value="uploadResult.error_count">
            <template #suffix><el-icon class="error-icon"><CircleClose /></el-icon></template>
          </el-statistic>
        </el-col>
      </el-row>

      <el-tabs v-if="uploadResult.errors.length > 0 || uploadResult.success_records.length > 0" style="margin-top: 20px;">
        <el-tab-pane v-if="uploadResult.errors.length > 0" label="错误详情" name="errors">
          <el-table :data="uploadResult.errors" border stripe>
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
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="成功记录" name="success">
          <el-table :data="uploadResult.success_records" border stripe>
            <el-table-column prop="patient_id" label="患者编号" width="120" />
            <el-table-column prop="patient_name" label="姓名" width="120" />
            <el-table-column prop="followup_date" label="随访日期" width="150">
              <template #default="{ row }">
                {{ formatDate(row.followup_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="score" label="评分" width="100" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTemplates } from '@/api/templates'
import { uploadRecords } from '@/api/records'
import dayjs from 'dayjs'

const uploadRef = ref(null)
const templates = ref([])
const uploading = ref(false)
const uploadResult = ref(null)
const currentFile = ref(null)

const form = ref({
  template_id: null
})

const canUpload = computed(() => form.value.template_id && currentFile.value)

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')

const fetchTemplates = async () => {
  try {
    templates.value = await getTemplates()
  } catch (e) {
    console.error(e)
  }
}

const handleFileChange = (file) => {
  currentFile.value = file.raw
}

const handleUpload = async () => {
  if (!canUpload.value) {
    ElMessage.warning('请选择模板和文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', currentFile.value)
    formData.append('template_id', form.value.template_id)

    uploadResult.value = await uploadRecords(formData)
    ElMessage.success('导入完成')
  } catch (e) {
    console.error(e)
  } finally {
    uploading.value = false
  }
}

const downloadTemplate = () => {
  const csvContent = 'patient_id,patient_name,followup_date,score\nP001,张三,2024-01-15,85\nP002,李四,2024-01-16,72\n'
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = '随访记录示例.csv'
  link.click()
}

onMounted(fetchTemplates)
</script>

<style scoped>
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.success-icon {
  color: #67c23a;
}

.error-icon {
  color: #f56c6c;
}
</style>
