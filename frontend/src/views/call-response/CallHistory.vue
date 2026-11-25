<template>
  <div class="call-history">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>呼叫历史</span>
          <el-form :inline="true">
            <el-form-item>
              <el-select v-model="filters.priority" placeholder="优先级" clearable>
                <el-option label="紧急" value="emergency" />
                <el-option label="普通" value="normal" />
                <el-option label="咨询" value="consultation" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select v-model="filters.status" placeholder="状态" clearable>
                <el-option label="已解决" value="resolved" />
                <el-option label="已取消" value="cancelled" />
                <el-option label="超时" value="timeout" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadData">查询</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <el-table :data="calls" v-loading="loading" stripe>
        <el-table-column prop="call_number" label="呼叫编号" width="160" />
        <el-table-column prop="caller_name" label="呼叫人" width="100" />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="CALL_PRIORITY[row.priority]?.type" size="small">
              {{ CALL_PRIORITY[row.priority]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="CALL_STATUS[row.status]?.type" size="small">
              {{ CALL_STATUS[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="call_time" label="呼叫时间" width="180" :formatter="(r) => formatDateTime(r.call_time)" />
        <el-table-column prop="response_duration" label="响应时长" width="120" :formatter="(r) => formatDuration(r.response_duration)" />
        <el-table-column prop="location_description" label="位置" />
      </el-table>

      <el-pagination
        v-model:current-page="page"
        :page-size="20"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getCalls } from '@/api/callResponse'
import { CALL_PRIORITY, CALL_STATUS } from '@/utils/constants'
import { formatDateTime, formatDuration } from '@/utils/formatters'

const calls = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const filters = reactive({ priority: '', status: '' })

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, ...filters }
    Object.keys(params).forEach((k) => { if (!params[k]) delete params[k] })
    const data = await getCalls(params)
    calls.value = data.results || data
    total.value = data.count || 0
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
