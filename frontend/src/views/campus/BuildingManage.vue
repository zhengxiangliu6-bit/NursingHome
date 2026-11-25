<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>楼栋管理</span>
          <el-button type="primary" @click="dialogVisible = true">添加楼栋</el-button>
        </div>
      </template>
      <el-table :data="buildings" v-loading="loading" stripe>
        <el-table-column prop="name" label="楼栋名称" />
        <el-table-column prop="code" label="编号" width="100" />
        <el-table-column prop="floors" label="楼层数" width="80" />
        <el-table-column prop="room_count" label="房间数" width="80" />
        <el-table-column prop="address" label="地址" />
        <el-table-column prop="description" label="描述" />
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加楼栋" width="500">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="编号"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="楼层数"><el-input-number v-model="form.floors" :min="1" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
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
import { getBuildings, createBuilding } from '@/api/campus'
import { ElMessage } from 'element-plus'

const buildings = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ name: '', code: '', floors: 5, address: '', description: '' })

async function loadData() {
  loading.value = true
  try {
    const data = await getBuildings()
    buildings.value = data.results || data
  } finally { loading.value = false }
}

async function handleSubmit() {
  await createBuilding(form)
  ElMessage.success('楼栋添加成功')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
