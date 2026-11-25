<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>巡更点管理</span>
          <el-button type="primary" @click="dialogVisible = true">添加巡更点</el-button>
        </div>
      </template>
      <el-table :data="checkpoints" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="building_name" label="楼栋" width="120" />
        <el-table-column prop="floor" label="楼层" width="80" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加巡更点" width="500">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="楼栋">
          <el-select v-model="form.building" placeholder="请选择">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="楼层"><el-input-number v-model="form.floor" :min="1" /></el-form-item>
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
import { getCheckpoints, createCheckpoint } from '@/api/patrol'
import { getBuildings } from '@/api/campus'
import { ElMessage } from 'element-plus'

const checkpoints = ref([])
const buildings = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ name: '', code: '', building: '', floor: 1, description: '' })

async function loadData() {
  loading.value = true
  try {
    const data = await getCheckpoints()
    checkpoints.value = data.results || data
  } finally { loading.value = false }
}

async function handleSubmit() {
  await createCheckpoint(form)
  ElMessage.success('巡更点添加成功')
  dialogVisible.value = false
  loadData()
}

onMounted(async () => {
  loadData()
  buildings.value = (await getBuildings()).results || await getBuildings()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
