<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
          <el-button type="primary" @click="dialogVisible = true">添加设备</el-button>
        </div>
      </template>
      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item>
          <el-select v-model="filters.device_category" placeholder="设备类别" clearable @change="loadData">
            <el-option label="摄像头" value="camera" />
            <el-option label="传感器" value="sensor" />
            <el-option label="广播设备" value="speaker" />
            <el-option label="呼叫设备" value="call_device" />
            <el-option label="定位信标" value="beacon" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.status" placeholder="状态" clearable @change="loadData">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="故障" value="fault" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="devices" v-loading="loading" stripe>
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="device_sn" label="序列号" width="150" />
        <el-table-column prop="device_category" label="类别" width="100" />
        <el-table-column prop="building_name" label="楼栋" width="100" />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="DEVICE_STATUS[row.status]?.type" size="small">
              {{ DEVICE_STATUS[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_maintenance" label="最近维护" width="120" />
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加设备" width="500">
      <el-form :model="form" label-width="100px">
        <el-form-item label="设备名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="序列号"><el-input v-model="form.device_sn" /></el-form-item>
        <el-form-item label="设备类别">
          <el-select v-model="form.device_category">
            <el-option label="摄像头" value="camera" />
            <el-option label="传感器" value="sensor" />
            <el-option label="广播设备" value="speaker" />
            <el-option label="呼叫设备" value="call_device" />
            <el-option label="定位信标" value="beacon" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP地址"><el-input v-model="form.ip_address" /></el-form-item>
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
import { getDevices, createDevice } from '@/api/campus'
import { DEVICE_STATUS } from '@/utils/constants'
import { ElMessage } from 'element-plus'

const devices = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const filters = reactive({ device_category: '', status: '' })
const form = reactive({ name: '', device_sn: '', device_category: 'sensor', ip_address: '' })

async function loadData() {
  loading.value = true
  try {
    const params = { ...filters }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    const data = await getDevices(params)
    devices.value = data.results || data
  } finally { loading.value = false }
}

async function handleSubmit() {
  await createDevice(form)
  ElMessage.success('设备添加成功')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
