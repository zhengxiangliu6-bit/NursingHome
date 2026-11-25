<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>床位调换申请</span>
          <el-button type="primary" @click="openCreate">新建申请</el-button>
        </div>
      </template>

      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item label="状态">
          <el-select v-model="filters.status" @change="loadData">
            <el-option label="全部" value="all" />
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="search" placeholder="搜索老人姓名" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="transfers" v-loading="loading" stripe>
        <el-table-column label="类型" width="70">
          <template #default="{ row }">
            <el-tag :type="row.resident_b ? 'warning' : ''" size="small">{{ row.transfer_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申请老人" width="100">
          <template #default="{ row }">{{ row.resident_a_name }}</template>
        </el-table-column>
        <el-table-column label="原床位" width="120">
          <template #default="{ row }">{{ row.bed_a_info }}</template>
        </el-table-column>
        <el-table-column width="40" align="center">
          <template #default="{ row }">{{ row.resident_b ? '⇄' : '→' }}</template>
        </el-table-column>
        <el-table-column label="目标床位" width="120">
          <template #default="{ row }">{{ row.target_bed_info }}</template>
        </el-table-column>
        <el-table-column label="对方老人" width="100">
          <template #default="{ row }">{{ row.resident_b_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" min-width="120" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagType[row.status]" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applicant_name" label="申请人" width="90" />
        <el-table-column prop="created_at" label="申请时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="handleApprove(row)">通过</el-button>
              <el-button size="small" type="danger" @click="openReject(row)">拒绝</el-button>
              <el-button size="small" @click="handleCancel(row)">取消</el-button>
            </template>
            <template v-else>
              <span v-if="row.reviewer_name" style="color:#909399; font-size:12px;">
                {{ row.reviewer_name }} 审批
              </span>
              <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建申请弹窗 -->
    <el-dialog v-model="createVisible" title="新建床位调换申请" width="520px" @closed="createFormRef?.clearValidate()">
      <el-form :model="createForm" label-width="100px" ref="createFormRef" :rules="createRules">
        <el-form-item label="申请老人" prop="resident_a">
          <el-select v-model="createForm.resident_a" filterable placeholder="选择老人" style="width:100%" @change="onResidentAChange">
            <el-option
              v-for="r in residentsWithBed"
              :key="r.id"
              :label="`${r.name}（${r.bed_info}）`"
              :value="r.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标床位" prop="target_bed">
          <el-select v-model="createForm.target_bed" filterable placeholder="选择目标床位" style="width:100%">
            <el-option-group label="空闲床位">
              <el-option
                v-for="b in availableTargetBeds"
                :key="b.id"
                :label="`${b.room_number}-${b.bed_number}（空闲）`"
                :value="b.id"
              />
            </el-option-group>
            <el-option-group label="已占用床位（将互换）">
              <el-option
                v-for="b in occupiedTargetBeds"
                :key="b.id"
                :label="`${b.room_number}-${b.bed_number}（${b.resident_name}）`"
                :value="b.id"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="调换预览">
          <div v-if="selectedA && createForm.target_bed" style="line-height:2;">
            <div style="color:#67C23A;">
              {{ selectedA.name }}：{{ selectedA.bed_info }} → {{ targetBedLabel }}
            </div>
            <div v-if="targetResident" style="color:#E6A23C;">
              {{ targetResident.name }}：{{ targetBedLabel }} → {{ selectedA.bed_info }}（互换）
            </div>
          </div>
          <span v-else style="color:#909399;">请选择老人和目标床位</span>
        </el-form-item>
        <el-form-item label="调换原因">
          <el-input v-model="createForm.reason" type="textarea" :rows="3" placeholder="请输入原因（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">提交申请</el-button>
      </template>
    </el-dialog>

    <!-- 拒绝弹窗 -->
    <el-dialog v-model="rejectVisible" title="拒绝调换申请" width="420px">
      <el-form label-width="100px">
        <el-form-item label="拒绝原因">
          <el-input v-model="rejectReason" type="textarea" :rows="3" placeholder="请输入拒绝原因（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" @click="handleReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getBedTransfers, createBedTransfer, approveBedTransfer,
  rejectBedTransfer, cancelBedTransfer, deleteBedTransfer, getResidents, getBeds,
} from '@/api/residents'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showAPIError } from '@/utils/errorHelper'

const transfers = ref([])
const loading = ref(false)
const search = ref('')
const filters = reactive({ status: 'all' })

const statusTagType = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  cancelled: 'info',
}

async function loadData() {
  loading.value = true
  try {
    const params = {}
    if (filters.status && filters.status !== 'all') params.status = filters.status
    if (search.value) params.search = search.value
    const data = await getBedTransfers(params)
    transfers.value = data.results || data
  } finally { loading.value = false }
}

// 新建申请
const createVisible = ref(false)
const createFormRef = ref(null)
const createForm = reactive({ resident_a: null, target_bed: null, reason: '' })
const createRules = {
  resident_a: [{ required: true, message: '请选择申请老人', trigger: 'change' }],
  target_bed: [{ required: true, message: '请选择目标床位', trigger: 'change' }],
}
const allResidents = ref([])
const allBeds = ref([])
const residentsWithBed = computed(() => allResidents.value.filter(r => r.status === 'active' && r.bed_info))

const selectedA = computed(() => residentsWithBed.value.find(r => r.id === createForm.resident_a))

// 目标床位：排除申请人当前床位
const availableTargetBeds = computed(() => {
  const currentBedId = selectedA.value?.bed
  return allBeds.value.filter(b => b.status === 'available' && b.id !== currentBedId)
})

// 已占用的床位（互换场景）：排除申请人自己的床位
const occupiedTargetBeds = computed(() => {
  const currentBedId = selectedA.value?.bed
  return allBeds.value
    .filter(b => b.status === 'occupied' && b.id !== currentBedId)
    .map(b => {
      const r = allResidents.value.find(res => res.bed === b.id && res.status === 'active')
      return { ...b, resident_name: r?.name || '未知' }
    })
})

const targetBedObj = computed(() => allBeds.value.find(b => b.id === createForm.target_bed))
const targetBedLabel = computed(() => {
  const b = targetBedObj.value
  return b ? `${b.room_number}-${b.bed_number}` : ''
})
const targetResident = computed(() => {
  if (!targetBedObj.value || targetBedObj.value.status !== 'occupied') return null
  return allResidents.value.find(r => r.bed === createForm.target_bed && r.status === 'active')
})

function onResidentAChange() {
  createForm.target_bed = null
}

function openCreate() {
  Object.assign(createForm, { resident_a: null, target_bed: null, reason: '' })
  createVisible.value = true
}

async function handleCreate() {
  try {
    await createFormRef.value.validate()
  } catch { return }
  try {
    await createBedTransfer(createForm)
    createVisible.value = false
    ElMessage.success('申请已提交')
    loadData()
    refreshOptions()
  } catch (e) {
    showAPIError(e, '提交失败')
  }
}

// 审批
async function handleApprove(row) {
  const desc = row.resident_b
    ? `将互换 ${row.resident_a_name}(${row.bed_a_info}) 和 ${row.resident_b_name}(${row.target_bed_info}) 的床位`
    : `将把 ${row.resident_a_name} 从 ${row.bed_a_info} 调换到 ${row.target_bed_info}`
  try {
    await ElMessageBox.confirm(`确认通过？${desc}。`, '确认通过', { type: 'warning' })
  } catch { return }
  try {
    await approveBedTransfer(row.id)
    ElMessage.success('已通过，床位已调换')
    loadData()
    refreshOptions()
  } catch (e) {
    showAPIError(e, '操作失败')
  }
}

// 拒绝
const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectingId = ref(null)

function openReject(row) {
  rejectingId.value = row.id
  rejectReason.value = ''
  rejectVisible.value = true
}

async function handleReject() {
  try {
    await rejectBedTransfer(rejectingId.value, { reason: rejectReason.value })
    rejectVisible.value = false
    ElMessage.success('已拒绝')
    loadData()
  } catch (e) {
    showAPIError(e, '操作失败')
  }
}

// 取消
async function handleCancel(row) {
  try {
    await ElMessageBox.confirm('确认取消该调换申请？', '确认取消', { type: 'info' })
  } catch { return }
  try {
    await cancelBedTransfer(row.id)
    ElMessage.success('已取消')
    loadData()
  } catch (e) {
    showAPIError(e, '操作失败')
  }
}

// 删除
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确认删除该调换申请记录？', '确认删除', { type: 'warning' })
  } catch { return }
  try {
    await deleteBedTransfer(row.id)
    ElMessage.success('已删除')
    loadData()
  } catch (e) {
    showAPIError(e, '删除失败')
  }
}

async function refreshOptions() {
  const [rData, bData] = await Promise.all([
    getResidents({ page_size: 999 }),
    getBeds(),
  ])
  allResidents.value = rData.results || rData
  allBeds.value = bData.results || bData
}

onMounted(async () => {
  loadData()
  refreshOptions()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
