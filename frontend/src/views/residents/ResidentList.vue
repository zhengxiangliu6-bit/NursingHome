<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>老人列表</span>
          <el-button type="primary" @click="$router.push({ name: 'ResidentDetail', params: { id: 'new' } })">新增老人</el-button>
        </div>
      </template>

      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item>
          <el-input v-model="search" placeholder="搜索姓名/身份证" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.status" placeholder="状态" clearable @change="loadData">
            <el-option label="在住" value="active" />
            <el-option label="离院" value="discharged" />
            <el-option label="住院中" value="hospitalized" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="residents" v-loading="loading" stripe @row-click="goDetail">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60">
          <template #default="{ row }">{{ row.gender === 'M' ? '男' : '女' }}</template>
        </el-table-column>
        <el-table-column prop="birth_date" label="出生日期" width="120" />
        <el-table-column prop="care_level_name" label="护理等级" width="100" />
        <el-table-column prop="bed_info" label="床位" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ { active: '在住', discharged: '离院', hospitalized: '住院中', deceased: '已故' }[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="admission_date" label="入住日期" width="120" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'discharged'"
              size="small" type="danger"
              @click.stop="handleDelete(row)"
            >删除</el-button>
          </template>
        </el-table-column>
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
import { useRouter } from 'vue-router'
import { getResidents, deleteResident } from '@/api/residents'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showAPIError } from '@/utils/errorHelper'

const router = useRouter()
const residents = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const search = ref('')
const filters = reactive({ status: '' })

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, search: search.value, ...filters }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    const data = await getResidents(params)
    residents.value = data.results || data
    total.value = data.count || 0
  } finally { loading.value = false }
}

function goDetail(row) {
  router.push({ name: 'ResidentDetail', params: { id: row.id } })
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.name} 的记录？此操作不可恢复。`, '确认删除', { type: 'warning' })
  } catch { return }
  try {
    await deleteResident(row.id)
    ElMessage.success('已删除')
    loadData()
  } catch (e) {
    showAPIError(e, '删除失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.el-table { cursor: pointer; }
</style>
