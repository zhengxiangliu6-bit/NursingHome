<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>健康检查记录</span>
          <el-button type="primary" @click="dialogVisible = true">新增检查</el-button>
        </div>
      </template>
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="resident_name" label="老人" width="100" />
        <el-table-column prop="checker_name" label="检查人" width="100" />
        <el-table-column prop="check_time" label="检查时间" width="180" />
        <el-table-column prop="check_type" label="检查类型" width="120" />
        <el-table-column prop="mental_status" label="精神状态" width="100" />
        <el-table-column prop="appetite" label="食欲" width="80" />
        <el-table-column prop="sleep_quality" label="睡眠" width="80" />
        <el-table-column prop="notes" label="备注" />
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增健康检查" width="600">
      <el-form :model="form" label-width="100px">
        <el-form-item label="老人">
          <el-select v-model="form.resident" filterable placeholder="请选择">
            <el-option v-for="r in residents" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检查类型">
          <el-select v-model="form.check_type">
            <el-option label="日常巡查" value="daily_round" />
            <el-option label="周检" value="weekly_checkup" />
            <el-option label="专项检查" value="special" />
          </el-select>
        </el-form-item>
        <el-form-item label="精神状态"><el-input v-model="form.mental_status" /></el-form-item>
        <el-form-item label="食欲"><el-input v-model="form.appetite" /></el-form-item>
        <el-form-item label="睡眠质量"><el-input v-model="form.sleep_quality" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getHealthChecks, createHealthCheck } from '@/api/smartDetection'
import { getResidents } from '@/api/residents'
import { ElMessage } from 'element-plus'

const records = ref([])
const residents = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({
  resident: '', check_type: 'daily_round', check_time: new Date().toISOString(),
  mental_status: '', appetite: '', sleep_quality: '', notes: '',
})

async function loadData() {
  loading.value = true
  try {
    const data = await getHealthChecks()
    records.value = data.results || data
  } finally { loading.value = false }
}

async function handleSubmit() {
  await createHealthCheck(form)
  ElMessage.success('检查记录已保存')
  dialogVisible.value = false
  loadData()
}

onMounted(async () => {
  loadData()
  const data = await getResidents({ status: 'active', page_size: 100 })
  residents.value = data.results || data
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
