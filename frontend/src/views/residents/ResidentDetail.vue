<template>
  <div v-loading="loading">
    <el-page-header @back="$router.back()" :content="resident?.name || '新增老人'" style="margin-bottom: 20px;" />

    <el-tabs v-model="activeTab">
      <!-- 基本信息 Tab -->
      <el-tab-pane label="基本信息" name="info">
        <el-card>
          <el-form :model="form" label-width="120px" :disabled="isView" ref="formRef" :rules="residentRules">
            <el-row :gutter="20">
              <!-- 照片上传 -->
              <el-col :span="4" style="display:flex; justify-content:center; align-items:flex-start; padding-top:4px;">
                <el-upload
                  class="avatar-uploader"
                  :show-file-list="false"
                  :before-upload="beforeUpload"
                  :http-request="handlePhotoUpload"
                  accept="image/*"
                >
                  <el-avatar v-if="form.photo" :src="form.photo" :size="80" shape="square" />
                  <el-icon v-else style="font-size:28px; color:#8c939d; width:80px; height:80px; border:1px dashed #d9d9d9; border-radius:4px; display:flex; align-items:center; justify-content:center;"><Plus /></el-icon>
                  <div style="font-size:12px; color:#909399; margin-top:4px; text-align:center;">点击上传照片</div>
                </el-upload>
              </el-col>
              <el-col :span="20">
                <el-row :gutter="20">
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
                    <el-form-item label="身份证号" prop="id_card"><el-input v-model="form.id_card" /></el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="出生日期" prop="birth_date">
                      <el-date-picker v-model="form.birth_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="入住日期" prop="admission_date">
                      <el-date-picker v-model="form.admission_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-col>
            </el-row>

            <el-divider content-position="left">照护信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="护理等级">
                  <el-select v-model="form.care_level" placeholder="请选择" clearable style="width:100%">
                    <el-option
                      v-for="cl in careLevels"
                      :key="cl.id"
                      :label="`${cl.name}（¥${cl.daily_rate}/天）`"
                      :value="cl.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="床位">
                  <el-select v-model="form.bed" placeholder="请选择" clearable style="width:100%">
                    <el-option
                      v-for="bed in availableBeds"
                      :key="bed.id"
                      :label="`${bed.room_number}-${bed.bed_number}`"
                      :value="bed.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="责任护士">
                  <el-select v-model="form.primary_nurse" placeholder="请选择" clearable style="width:100%" filterable>
                    <el-option v-for="n in nurses" :key="n.id" :label="`${n.last_name}${n.first_name}`" :value="n.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">联系人</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="紧急联系人" prop="emergency_contact_name"><el-input v-model="form.emergency_contact_name" /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="紧急联系电话" prop="emergency_contact_phone"><el-input v-model="form.emergency_contact_phone" /></el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">医疗信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="既往病史"><el-input v-model="form.medical_history" type="textarea" :rows="3" /></el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="过敏信息"><el-input v-model="form.allergy_info" type="textarea" /></el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" /></el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button type="primary" @click="handleSave">保存</el-button>
              <el-button
                v-if="residentId !== 'new' && form.status === 'active' && !currentLeave"
                type="warning"
                @click="leaveVisible = true"
              >请假</el-button>
              <el-button
                v-if="currentLeave"
                type="success"
                @click="handleEndLeave"
              >销假</el-button>
              <el-tag v-if="currentLeave" type="warning" size="large" style="margin-left:12px;">
                请假中（{{ currentLeave.start_date }} 起）
              </el-tag>
              <el-button
                v-if="residentId !== 'new' && form.status !== 'discharged' && !currentLeave"
                type="danger"
                @click="dischargeVisible = true"
              >办理退住</el-button>
              <el-tag v-if="form.status === 'discharged'" type="info" size="large" style="margin-left:12px;">
                已退住（{{ form.discharge_date }}）
              </el-tag>
              <el-button
                v-if="form.status === 'discharged'"
                type="danger"
                plain
                @click="handleDeleteResident"
                style="margin-left:12px;"
              >删除记录</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 家属联系人 Tab -->
      <el-tab-pane label="家属联系人" name="family" v-if="residentId !== 'new'">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>家属联系人</span>
              <el-button type="primary" size="small" @click="openAddFamily">添加家属</el-button>
            </div>
          </template>
          <el-table :data="familyRelations" stripe>
            <el-table-column label="姓名" width="120">
              <template #default="{ row }">{{ row.family_user_name }}</template>
            </el-table-column>
            <el-table-column prop="relationship" label="关系" width="100" />
            <el-table-column label="主要联系人" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_primary_contact" type="success" size="small">是</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="接收告警" width="100">
              <template #default="{ row }">
                <el-tag :type="row.can_receive_alerts ? 'success' : 'info'" size="small">
                  {{ row.can_receive_alerts ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="removeFamily(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 生命体征 Tab -->
      <el-tab-pane label="生命体征" name="vitals" v-if="residentId !== 'new'">
        <el-card>
          <el-table :data="vitals" stripe>
            <el-table-column prop="measured_at" label="测量时间" width="180" />
            <el-table-column prop="heart_rate" label="心率" width="80" />
            <el-table-column prop="systolic_bp" label="收缩压" width="80" />
            <el-table-column prop="diastolic_bp" label="舒张压" width="80" />
            <el-table-column prop="blood_oxygen" label="血氧" width="80" />
            <el-table-column prop="temperature" label="体温" width="80" />
            <el-table-column prop="is_abnormal" label="异常" width="60">
              <template #default="{ row }">
                <el-tag v-if="row.is_abnormal" type="danger" size="small">异常</el-tag>
                <el-tag v-else type="success" size="small">正常</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 护理评估 Tab -->
      <el-tab-pane label="护理评估" name="assessments" v-if="residentId !== 'new'">
        <el-card>
          <el-table :data="assessments" stripe>
            <el-table-column prop="assessment_date" label="评估日期" width="180" />
            <el-table-column prop="assessor_name" label="评估人" width="100" />
            <el-table-column prop="overall_score" label="综合评分" width="100" />
            <el-table-column prop="recommended_level_name" label="建议等级" width="100" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="{ draft: 'info', submitted: 'warning', approved: 'success' }[row.status]" size="small">
                  {{ { draft: '草稿', submitted: '已提交', approved: '已审核' }[row.status] }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 请假记录 Tab -->
      <el-tab-pane label="请假记录" name="leaves" v-if="residentId !== 'new'">
        <el-card>
          <el-table :data="leaveRecords" stripe>
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="expected_return_date" label="预计返回" width="120">
              <template #default="{ row }">{{ row.expected_return_date || '-' }}</template>
            </el-table-column>
            <el-table-column prop="actual_return_date" label="实际返回" width="120">
              <template #default="{ row }">{{ row.actual_return_date || '-' }}</template>
            </el-table-column>
            <el-table-column prop="reason" label="请假原因" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="{ on_leave: 'warning', returned: 'success', cancelled: 'info' }[row.status]" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="handler_name" label="操作人" width="100">
              <template #default="{ row }">{{ row.handler_name || '-' }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加家属弹窗 -->
    <el-dialog v-model="familyFormVisible" title="添加家属联系人" width="420px">
      <el-alert type="info" :closable="false" style="margin-bottom: 12px;">
        需要先为家属在系统中创建"家属"角色账号，再关联到老人。
      </el-alert>
      <el-form :model="familyForm" label-width="100px">
        <el-form-item label="家属账号">
          <el-select v-model="familyForm.family_user" filterable placeholder="搜索家属用户" style="width:100%">
            <el-option v-for="u in familyUsers" :key="u.id" :label="`${u.last_name}${u.first_name}（${u.phone}）`" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关系">
          <el-select v-model="familyForm.relationship" style="width:100%">
            <el-option label="子女" value="子女" />
            <el-option label="配偶" value="配偶" />
            <el-option label="兄弟姐妹" value="兄弟姐妹" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="主要联系人">
          <el-switch v-model="familyForm.is_primary_contact" />
        </el-form-item>
        <el-form-item label="接收告警">
          <el-switch v-model="familyForm.can_receive_alerts" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="familyFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddFamily">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- 请假弹窗 -->
    <el-dialog v-model="leaveVisible" title="办理请假" width="420px">
      <el-alert type="info" :closable="false" style="margin-bottom:16px;">
        请假期间床位将保留，标记为"请假"状态，不会被分配给其他人。
      </el-alert>
      <el-form :model="leaveForm" label-width="100px">
        <el-form-item label="开始日期">
          <el-date-picker v-model="leaveForm.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="预计返回">
          <el-date-picker v-model="leaveForm.expected_return_date" type="date" value-format="YYYY-MM-DD" placeholder="选填" style="width:100%" />
        </el-form-item>
        <el-form-item label="请假原因">
          <el-input v-model="leaveForm.reason" type="textarea" :rows="3" placeholder="请输入请假原因（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="leaveVisible = false">取消</el-button>
        <el-button type="warning" @click="handleStartLeave">确认请假</el-button>
      </template>
    </el-dialog>

    <!-- 退住弹窗 -->
    <el-dialog v-model="dischargeVisible" title="办理退住" width="420px">
      <el-alert type="warning" :closable="false" style="margin-bottom:16px;">
        退住后将释放该老人的床位，状态变更为"离院"。此操作不可撤销。
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getResident, createResident, updateResident, deleteResident, getResidentAssessments,
  getCareLevels, getBeds, dischargeResident, startLeave, endLeave, getResidentLeaves,
} from '@/api/residents'
import { getVitalTrends } from '@/api/smartDetection'
import { getUsers, createFamilyRelation, deleteFamilyRelation, getFamilyRelations } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showAPIError } from '@/utils/errorHelper'
import { Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const residentId = computed(() => route.params.id)
const loading = ref(false)
const activeTab = ref('info')
const resident = ref(null)
const vitals = ref([])
const assessments = ref([])
const isView = ref(false)
const careLevels = ref([])
const allBeds = ref([])
// 下拉框显示：空闲的床位 + 当前老人已占用的床位（否则会显示 UUID）
const availableBeds = computed(() => {
  return allBeds.value.filter(b => b.status === 'available' || b.id === form.bed)
})
const nurses = ref([])
const familyRelations = ref([])
const familyUsers = ref([])
const familyFormVisible = ref(false)
const familyForm = reactive({
  family_user: '', relationship: '子女', is_primary_contact: false, can_receive_alerts: true,
})

const dischargeVisible = ref(false)
const dischargeForm = reactive({
  discharge_date: new Date().toISOString().slice(0, 10),
  reason: '',
})

const leaveVisible = ref(false)
const leaveForm = reactive({
  start_date: new Date().toISOString().slice(0, 10),
  expected_return_date: null,
  reason: '',
})
const leaveRecords = ref([])
const currentLeave = computed(() => leaveRecords.value.find(l => l.status === 'on_leave') || null)

const formRef = ref(null)
const residentRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  id_card: [{ required: true, message: '请输入身份证号', trigger: 'blur' }],
  birth_date: [{ required: true, message: '请选择出生日期', trigger: 'change' }],
  admission_date: [{ required: true, message: '请选择入住日期', trigger: 'change' }],
  emergency_contact_name: [{ required: true, message: '请输入紧急联系人', trigger: 'blur' }],
  emergency_contact_phone: [{ required: true, message: '请输入紧急联系电话', trigger: 'blur' }],
}

const form = reactive({
  name: '', gender: 'M', id_card: '', birth_date: '', phone: '',
  admission_date: '', emergency_contact_name: '', emergency_contact_phone: '',
  medical_history: '', allergy_info: '', notes: '',
  care_level: null, bed: null, primary_nurse: null, photo: null,
})

async function loadResident() {
  if (residentId.value === 'new') return
  loading.value = true
  try {
    const data = await getResident(residentId.value)
    resident.value = data
    Object.assign(form, data)
    form.care_level = data.care_level || null
    form.bed = data.bed || null
    form.primary_nurse = data.primary_nurse || null

    const [vData, aData, frData, lData] = await Promise.all([
      getVitalTrends(residentId.value, { days: 30 }),
      getResidentAssessments(residentId.value),
      getFamilyRelations({ resident: residentId.value }),
      getResidentLeaves(residentId.value),
    ])
    vitals.value = Array.isArray(vData) ? vData : (vData.results || [])
    assessments.value = Array.isArray(aData) ? aData : (aData.results || [])
    familyRelations.value = frData.results || frData
    leaveRecords.value = Array.isArray(lData) ? lData : (lData.results || [])
  } finally { loading.value = false }
}

async function handleSave() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  try {
    const payload = { ...form }
    if (!payload.photo || typeof payload.photo === 'string') delete payload.photo
    if (residentId.value === 'new') {
      await createResident(payload)
      ElMessage.success('老人信息已创建')
      router.push('/residents')
    } else {
      await updateResident(residentId.value, payload)
      ElMessage.success('信息已更新')
      router.push('/residents')
    }
  } catch (e) {
    showAPIError(e, '保存失败')
  }
}

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  if (!isImage) ElMessage.error('请上传图片文件')
  return isImage
}

async function handlePhotoUpload({ file }) {
  if (residentId.value === 'new') {
    form.photo = URL.createObjectURL(file)
    return
  }
  const formData = new FormData()
  formData.append('photo', file)
  try {
    await updateResident(residentId.value, formData)
    form.photo = URL.createObjectURL(file)
    ElMessage.success('照片已上传')
  } catch { ElMessage.error('照片上传失败') }
}

function openAddFamily() {
  Object.assign(familyForm, { family_user: '', relationship: '子女', is_primary_contact: false, can_receive_alerts: true })
  familyFormVisible.value = true
}

async function handleAddFamily() {
  try {
    await createFamilyRelation({ ...familyForm, resident: residentId.value })
    ElMessage.success('已添加')
    familyFormVisible.value = false
    const frData = await getFamilyRelations({ resident: residentId.value })
    familyRelations.value = frData.results || frData
  } catch (e) {
    showAPIError(e, '添加失败')
  }
}

async function removeFamily(row) {
  await ElMessageBox.confirm('确认移除此家属？', '提示', { type: 'warning' })
  await deleteFamilyRelation(row.id)
  ElMessage.success('已移除')
  familyRelations.value = familyRelations.value.filter(r => r.id !== row.id)
}

async function handleDeleteResident() {
  try {
    await ElMessageBox.confirm('确认删除该老人记录？此操作不可恢复。', '确认删除', { type: 'warning' })
  } catch { return }
  try {
    await deleteResident(residentId.value)
    ElMessage.success('记录已删除')
    router.push('/residents')
  } catch (e) {
    showAPIError(e, '删除失败')
  }
}

async function handleDischarge() {
  try {
    await ElMessageBox.confirm('确认办理退住？退住后将释放床位，此操作不可撤销。', '确认退住', { type: 'warning' })
  } catch { return }
  try {
    await dischargeResident(residentId.value, dischargeForm)
    dischargeVisible.value = false
    ElMessage.success('已办理退住')
    router.push('/residents')
  } catch (e) {
    showAPIError(e, '退住失败')
  }
}

async function loadLeaves() {
  if (residentId.value === 'new') return
  try {
    const data = await getResidentLeaves(residentId.value)
    leaveRecords.value = Array.isArray(data) ? data : (data.results || [])
  } catch { /* ignore */ }
}

async function handleStartLeave() {
  try {
    await startLeave(residentId.value, leaveForm)
    leaveVisible.value = false
    ElMessage.success('已办理请假')
    loadLeaves()
  } catch (e) {
    showAPIError(e, '请假失败')
  }
}

async function handleEndLeave() {
  try {
    await ElMessageBox.confirm('确认销假？床位状态将恢复为"已占用"。', '确认销假', { type: 'info' })
  } catch { return }
  try {
    await endLeave(residentId.value, { actual_return_date: new Date().toISOString().slice(0, 10) })
    ElMessage.success('已销假')
    loadLeaves()
  } catch (e) {
    showAPIError(e, '销假失败')
  }
}

onMounted(async () => {
  loadResident()
  const [clData, bedData, staffData] = await Promise.all([
    getCareLevels(),
    getBeds(),
    getUsers(),
  ])
  careLevels.value = clData.results || clData
  allBeds.value = bedData.results || bedData
  const allStaff = staffData.results || staffData
  nurses.value = allStaff.filter(u => u.role_name === '护士' || u.role_name === '护工')
  familyUsers.value = allStaff.filter(u => u.role_name === '家属')
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
