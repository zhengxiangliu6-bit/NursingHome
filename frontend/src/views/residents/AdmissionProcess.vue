<template>
  <div class="admission-process">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>入住退住流程</span>
          <el-button type="primary" @click="openCreate">新建咨询</el-button>
        </div>
      </template>

      <!-- 阶段筛选 -->
      <el-tabs v-model="activeStage" @tab-change="loadData">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="咨询中" name="consulting" />
        <el-tab-pane label="评估中" name="assessing" />
        <el-tab-pane label="签约中" name="contracting" />
        <el-tab-pane label="已完成" name="admitted" />
        <el-tab-pane label="已拒绝" name="rejected" />
        <el-tab-pane label="已撤销" name="withdrawn" />
      </el-tabs>

      <!-- 搜索 -->
      <el-form :inline="true" style="margin-bottom: 12px;">
        <el-form-item>
          <el-input v-model="search" placeholder="搜索姓名/电话" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="applications" v-loading="loading" stripe @row-click="openDetail">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender_display" label="性别" width="60" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="stage_display" label="阶段" width="100">
          <template #default="{ row }">
            <el-tag :type="stageTagType(row.stage)" size="small">{{ row.stage_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预留床位" width="100">
          <template #default="{ row }">
            <span v-if="row.reserved_bed_info">{{ row.reserved_bed_info }}</span>
            <span v-else style="color:#909399">-</span>
          </template>
        </el-table-column>
        <el-table-column label="老人状态" width="100">
          <template #default="{ row }">
            <template v-if="row.stage === 'admitted' && row.resident_name">
              <el-tag :type="row.resident_status === 'active' ? 'success' : 'info'" size="small">
                {{ { active: '在住', discharged: '已退住' }[row.resident_status] || row.resident_status }}
              </el-tag>
            </template>
            <span v-else style="color:#909399">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ row.created_at?.slice(0, 16) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button
                v-if="['consulting','assessing'].includes(row.stage)"
                size="small" type="primary"
                @click.stop="handleAdvance(row)"
              >推进</el-button>
              <el-button
                v-if="row.stage === 'contracting'"
                size="small" type="success"
                @click.stop="openAdmit(row)"
              >办理入住</el-button>
              <el-button
                v-if="row.stage === 'admitted' && row.resident_status === 'active'"
                size="small" type="warning"
                @click.stop="openDischarge(row)"
              >办理退住</el-button>
              <el-button
                v-if="!['admitted','rejected','withdrawn'].includes(row.stage)"
                size="small"
                @click.stop="openEdit(row)"
              >编辑</el-button>
              <el-button
                v-if="!['admitted','rejected','withdrawn'].includes(row.stage)"
                size="small" type="danger"
                @click.stop="handleReject(row)"
              >拒绝</el-button>
              <el-button
                v-if="!(row.stage === 'admitted' && row.resident_status === 'active')"
                size="small" type="danger" plain
                @click.stop="handleDeleteApp(row)"
              >删除</el-button>
            </div>
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

    <!-- 创建/编辑弹窗 -->
    <el-dialog v-model="formVisible" :title="editingId ? '编辑申请' : '新建咨询'" width="550px" @closed="formRef?.clearValidate()">
      <el-form :model="form" label-width="110px" ref="formRef" :rules="formRules">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name"><el-input v-model="form.name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="form.gender">
                <el-radio value="M">男</el-radio>
                <el-radio value="F">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker v-model="form.birth_date" type="date" value-format="YYYY-MM-DD" style="width:100%"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone"><el-input v-model="form.phone" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="紧急联系人"><el-input v-model="form.emergency_contact_name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="紧急电话"><el-input v-model="form.emergency_contact_phone" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="来源渠道"><el-input v-model="form.inquiry_source" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计入住日期">
              <el-date-picker v-model="form.expected_admission_date" type="date" value-format="YYYY-MM-DD" style="width:100%"/>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="预留床位">
              <el-select v-model="form.reserved_bed" clearable placeholder="可选择预留床位" style="width:100%">
                <el-option
                  v-for="bed in selectableBeds"
                  :key="bed.id"
                  :label="`${bed.room_number}-${bed.bed_number}`"
                  :value="bed.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="申请详情" width="620px">
      <div v-if="detailApp">
        <el-steps
          :active="stageStep(detailApp.stage)"
          finish-status="success"
          style="margin-bottom: 20px;"
        >
          <el-step title="咨询" />
          <el-step title="评估" />
          <el-step title="签约" />
          <el-step title="入住" />
        </el-steps>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ detailApp.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ detailApp.gender_display }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ detailApp.phone }}</el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ detailApp.birth_date }}</el-descriptions-item>
          <el-descriptions-item label="紧急联系人">{{ detailApp.emergency_contact_name }}</el-descriptions-item>
          <el-descriptions-item label="紧急电话">{{ detailApp.emergency_contact_phone }}</el-descriptions-item>
          <el-descriptions-item label="来源渠道">{{ detailApp.inquiry_source }}</el-descriptions-item>
          <el-descriptions-item label="预计入住">{{ detailApp.expected_admission_date }}</el-descriptions-item>
          <el-descriptions-item label="预留床位">{{ detailApp.reserved_bed_info || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ detailApp.notes }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="detailApp.resident_name" style="margin-top: 12px; font-weight:500;">
          <el-tag :type="detailApp.resident_status === 'active' ? 'success' : 'info'" style="margin-right:8px;">
            {{ detailApp.resident_status === 'active' ? '在住' : '已退住' }}
          </el-tag>
          已关联老人档案：{{ detailApp.resident_name }}
        </div>
      </div>
    </el-dialog>

    <!-- 办理入住弹窗 -->
    <el-dialog v-model="admitVisible" title="确认办理入住" width="460px">
      <el-form :model="admitForm" label-width="110px">
        <el-form-item label="身份证号" required>
          <el-input v-model="admitForm.id_card" placeholder="请输入身份证号" maxlength="18" />
        </el-form-item>
        <el-form-item label="入住日期" required>
          <el-date-picker v-model="admitForm.admission_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="分配床位">
          <el-select v-model="admitForm.bed_id" clearable placeholder="请选择（可稍后在老人档案中设置）" style="width:100%">
            <el-option
              v-for="bed in selectableBeds"
              :key="bed.id"
              :label="`${bed.room_number}-${bed.bed_number}`"
              :value="bed.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="护理等级">
          <el-select v-model="admitForm.care_level_id" clearable placeholder="请选择（可稍后设置）" style="width:100%">
            <el-option
              v-for="cl in careLevels"
              :key="cl.id"
              :label="`${cl.name}（¥${cl.daily_rate}/天）`"
              :value="cl.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="责任护士">
          <el-select v-model="admitForm.primary_nurse_id" clearable placeholder="请选择（可稍后设置）" style="width:100%" filterable>
            <el-option v-for="n in nurses" :key="n.id" :label="`${n.last_name}${n.first_name}`" :value="n.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="admitVisible = false">取消</el-button>
        <el-button type="success" @click="handleAdmit">确认入住</el-button>
      </template>
    </el-dialog>

    <!-- 办理退住弹窗 -->
    <el-dialog v-model="dischargeVisible" title="办理退住" width="420px">
      <el-alert type="warning" :closable="false" style="margin-bottom:16px;">
        退住后将释放该老人的床位（进入清洁中状态），状态变更为"离院"。
      </el-alert>
      <el-form :model="dischargeForm" label-width="100px">
        <el-form-item label="退住日期">
          <el-date-picker v-model="dischargeForm.discharge_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="退住原因">
          <el-input v-model="dischargeForm.reason" type="textarea" :rows="3" placeholder="请输入退住原因（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dischargeVisible = false">取消</el-button>
        <el-button type="danger" @click="handleDischarge">确认退住</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getAdmissionApplications, createAdmissionApplication,
  updateAdmissionApplication, deleteAdmissionApplication,
  advanceApplicationStage, rejectApplication,
  admitApplication, dischargeApplication,
  getAvailableBeds, getCareLevels, getBeds,
} from '@/api/residents'
import { getUsers } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showAPIError } from '@/utils/errorHelper'

const applications = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const search = ref('')
const activeStage = ref('')

const allBeds = ref([])
const careLevels = ref([])
const nurses = ref([])

// 可选择的床位：空闲 + 预留的（当前编辑的申请所预留的也要显示出来）
const selectableBeds = computed(() => {
  return allBeds.value.filter(b => b.status === 'available' || b.status === 'reserved')
})

const formRef = ref(null)
const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
}

const formVisible = ref(false)
const editingId = ref(null)
const form = reactive({
  name: '', gender: 'M', birth_date: '', phone: '',
  emergency_contact_name: '', emergency_contact_phone: '',
  inquiry_source: '', notes: '', expected_admission_date: '',
  reserved_bed: null,
})

const detailVisible = ref(false)
const detailApp = ref(null)

const admitVisible = ref(false)
const admitingApp = ref(null)
const admitForm = reactive({
  id_card: '',
  admission_date: new Date().toISOString().slice(0, 10),
  bed_id: null,
  care_level_id: null,
  primary_nurse_id: null,
})

const dischargeVisible = ref(false)
const dischargingApp = ref(null)
const dischargeForm = reactive({
  discharge_date: new Date().toISOString().slice(0, 10),
  reason: '',
})

const stageOrder = ['consulting', 'assessing', 'contracting', 'admitted']

function stageStep(s) {
  if (s === 'admitted') return 4
  const idx = stageOrder.indexOf(s)
  return idx >= 0 ? idx : 0
}

function stageTagType(s) {
  return { consulting: '', assessing: 'warning', contracting: 'success', admitted: 'success', rejected: 'danger', withdrawn: 'info' }[s] || ''
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, search: search.value }
    if (activeStage.value) params.stage = activeStage.value
    const data = await getAdmissionApplications(params)
    applications.value = data.results || data
    total.value = data.count || 0
  } finally { loading.value = false }
}

async function loadBeds() {
  const bedData = await getBeds()
  allBeds.value = bedData.results || bedData
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    name: '', gender: 'M', birth_date: '', phone: '',
    emergency_contact_name: '', emergency_contact_phone: '',
    inquiry_source: '', notes: '', expected_admission_date: '',
    reserved_bed: null,
  })
  formVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name, gender: row.gender, birth_date: row.birth_date, phone: row.phone,
    emergency_contact_name: row.emergency_contact_name, emergency_contact_phone: row.emergency_contact_phone,
    inquiry_source: row.inquiry_source, notes: row.notes, expected_admission_date: row.expected_admission_date,
    reserved_bed: row.reserved_bed || null,
  })
  formVisible.value = true
}

function openDetail(row) {
  detailApp.value = row
  detailVisible.value = true
}

async function handleSave() {
  try {
    await formRef.value.validate()
  } catch { return }
  try {
    if (editingId.value) {
      await updateAdmissionApplication(editingId.value, form)
      ElMessage.success('已更新')
    } else {
      await createAdmissionApplication(form)
      ElMessage.success('咨询已创建')
    }
    formVisible.value = false
    loadData()
    loadBeds()
  } catch (e) { showAPIError(e, '保存失败') }
}

async function handleAdvance(row) {
  await advanceApplicationStage(row.id)
  ElMessage.success('已推进到下一阶段')
  loadData()
}

async function handleReject(row) {
  await ElMessageBox.confirm(`确认拒绝 ${row.name} 的申请？`, '提示', { type: 'warning' })
  await rejectApplication(row.id, {})
  ElMessage.success('已拒绝')
  loadData()
  loadBeds()
}

function openAdmit(row) {
  admitingApp.value = row
  Object.assign(admitForm, {
    id_card: '',
    admission_date: new Date().toISOString().slice(0, 10),
    bed_id: row.reserved_bed || null,
    care_level_id: null, primary_nurse_id: null,
  })
  admitVisible.value = true
}

async function handleAdmit() {
  try {
    await admitApplication(admitingApp.value.id, admitForm)
    ElMessage.success('入住办理成功，老人档案已创建')
    admitVisible.value = false
    loadData()
    loadBeds()
  } catch (e) {
    showAPIError(e, '入住办理失败')
  }
}

function openDischarge(row) {
  dischargingApp.value = row
  Object.assign(dischargeForm, {
    discharge_date: new Date().toISOString().slice(0, 10),
    reason: '',
  })
  dischargeVisible.value = true
}

async function handleDischarge() {
  try {
    await ElMessageBox.confirm('确认办理退住？退住后将释放床位。', '确认退住', { type: 'warning' })
  } catch { return }
  try {
    await dischargeApplication(dischargingApp.value.id, dischargeForm)
    ElMessage.success('已办理退住')
    dischargeVisible.value = false
    loadData()
    loadBeds()
  } catch (e) {
    showAPIError(e, '退住失败')
  }
}

async function handleDeleteApp(row) {
  await ElMessageBox.confirm(`确认删除 ${row.name} 的记录？此操作不可恢复。`, '提示', { type: 'warning' })
  try {
    await deleteAdmissionApplication(row.id)
    ElMessage.success('已删除')
    loadData()
    loadBeds()
  } catch (e) {
    showAPIError(e, '删除失败')
  }
}

onMounted(async () => {
  loadData()
  const [bedData, clData, staffData] = await Promise.all([
    getBeds(),
    getCareLevels(),
    getUsers(),
  ])
  allBeds.value = bedData.results || bedData
  careLevels.value = clData.results || clData
  const all = staffData.results || staffData
  nurses.value = all.filter(u => u.role_name === '护士' || u.role_name === '护工')
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.el-table { cursor: pointer; }
.action-btns { display: flex; flex-wrap: wrap; gap: 4px; }
.action-btns .el-button { margin-left: 0; }
</style>
