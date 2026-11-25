<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>呼叫设备管理</span>
          <el-button type="primary" @click="dialogVisible = true">添加设备</el-button>
        </div>
      </template>
      <el-table :data="devices" v-loading="loading" stripe>
        <el-table-column prop="device_sn" label="序列号" width="180" />
        <el-table-column prop="device_type" label="类型" width="120" />
        <el-table-column prop="resident_name" label="绑定老人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加呼叫设备" width="500">
      <el-form :model="form" label-width="100px">
        <el-form-item label="序列号"><el-input v-model="form.device_sn" /></el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="form.device_type">
            <el-option label="床头呼叫器" value="bedside" />
            <el-option label="随身挂件" value="pendant" />
            <el-option label="墙壁按钮" value="wall" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getCallDevices, createCallDevice } from '@/api/callResponse'
import { ElMessage } from 'element-plus'

const devices = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ device_sn: '', device_type: 'bedside' })

async function loadData() {
  loading.value = true
  try {
    const data = await getCallDevices()
    devices.value = data.results || data
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await createCallDevice(form)
  ElMessage.success('设备添加成功')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
