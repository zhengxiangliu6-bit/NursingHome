<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工档案</span>
          <el-button type="primary" @click="openCreate">新增员工</el-button>
        </div>
      </template>

      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item>
          <el-input v-model="search" placeholder="搜索姓名/工号" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.role" placeholder="角色" clearable @change="loadData" style="width:120px">
            <el-option v-for="r in roles" :key="r.id" :label="r.display_name || r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.is_active" placeholder="状态" clearable @change="loadData" style="width:100px">
            <el-option label="在职" :value="true" />
            <el-option label="离职" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="staff" v-loading="loading" stripe>
        <el-table-column prop="last_name" label="姓名" width="100">
          <template #default="{ row }">{{ row.last_name }}{{ row.first_name }}</template>
        </el-table-column>
        <el-table-column prop="employee_id" label="工号" width="100" />
        <el-table-column prop="role_name" label="角色" width="100" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="phone" label="手机" width="130" />
        <el-table-column label="职称" width="100">
          <template #default="{ row }">{{ profileMap[row.id]?.title }}</template>
        </el-table-column>
        <el-table-column label="所属楼栋" width="100">
          <template #default="{ row }">{{ profileMap[row.id]?.building_name }}</template>
        </el-table-column>
        <el-table-column label="在岗" width="80">
          <template #default="{ row }">
            <el-tag :type="profileMap[row.id]?.on_duty ? 'success' : 'info'" size="small">
              {{ profileMap[row.id]?.on_duty ? '在岗' : '休息' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '在职' : '已离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDisable(row)" v-if="row.is_active">禁用</el-button>
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="formVisible" :title="editingId ? '编辑员工' : '新增员工'" width="560px" @closed="staffFormRef?.clearValidate()">
      <el-form :model="form" label-width="90px" ref="staffFormRef" :rules="staffFormRules">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓" prop="last_name"><el-input v-model="form.last_name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名"><el-input v-model="form.first_name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户名" prop="username"><el-input v-model="form.username" :disabled="!!editingId" /></el-form-item>
          </el-col>
          <el-col :span="12" v-if="!editingId">
            <el-form-item label="密码" prop="password"><el-input v-model="form.password" type="password" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机"><el-input v-model="form.phone" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号"><el-input v-model="form.employee_id" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select v-model="form.role" style="width:100%">
                <el-option v-for="r in staffRoles" :key="r.id" :label="r.display_name || r.name" :value="r.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门"><el-input v-model="form.department" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称"><el-input v-model="form.profile_title" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资质证书"><el-input v-model="form.profile_certification" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属楼栋">
              <el-select v-model="form.profile_building" clearable style="width:100%">
                <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="在岗状态">
              <el-switch v-model="form.profile_on_duty" active-text="在岗" inactive-text="休息" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getUsers, createUser, updateUser, getRoles,
  getStaffProfiles, createStaffProfile, updateStaffProfile,
} from '@/api/auth'
import { getBuildings } from '@/api/campus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showAPIError } from '@/utils/errorHelper'

const staff = ref([])
const profiles = ref([])
const roles = ref([])
const buildings = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const search = ref('')
const filters = reactive({ role: '', is_active: '' })

const staffFormRef = ref(null)
const staffFormRules = computed(() => ({
  last_name: [{ required: true, message: '请输入姓', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: editingId.value ? [] : [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}))

const formVisible = ref(false)
const editingId = ref(null)
const form = reactive({
  username: '', password: '', first_name: '', last_name: '', phone: '',
  employee_id: '', role: '', department: '',
  profile_title: '', profile_certification: '', profile_building: null, profile_on_duty: false,
})

const profileMap = computed(() => {
  const map = {}
  profiles.value.forEach(p => { map[p.user] = p })
  return map
})

const NON_STAFF_ROLES = ['family_member']
const staffRoles = computed(() => roles.value.filter(r => !NON_STAFF_ROLES.includes(r.name)))

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, search: search.value }
    if (filters.role) params.role = filters.role
    if (filters.is_active !== '') params.is_active = filters.is_active
    const data = await getUsers(params)
    staff.value = (data.results || data).filter(u => u.role_name !== '家属')
    total.value = data.count || 0

    const pData = await getStaffProfiles()
    profiles.value = pData.results || pData
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    username: '', password: '', first_name: '', last_name: '', phone: '',
    employee_id: '', role: '', department: '',
    profile_title: '', profile_certification: '', profile_building: null, profile_on_duty: false,
  })
  formVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  const profile = profileMap.value[row.id] || {}
  Object.assign(form, {
    username: row.username,
    first_name: row.first_name,
    last_name: row.last_name,
    phone: row.phone,
    employee_id: row.employee_id,
    role: row.role,
    department: row.department,
    profile_title: profile.title || '',
    profile_certification: profile.certification || '',
    profile_building: profile.assigned_building || null,
    profile_on_duty: profile.on_duty || false,
  })
  formVisible.value = true
}

async function handleSave() {
  try {
    await staffFormRef.value.validate()
  } catch {
    return
  }
  try {
    const userData = {
      username: form.username, first_name: form.first_name, last_name: form.last_name,
      phone: form.phone, employee_id: form.employee_id, role: form.role, department: form.department,
    }
    let userId = editingId.value
    if (editingId.value) {
      await updateUser(editingId.value, userData)
    } else {
      const res = await createUser({ ...userData, password: form.password })
      userId = res.id
    }
    // 处理员工扩展信息
    const profileData = {
      user: userId,
      title: form.profile_title,
      certification: form.profile_certification,
      assigned_building: form.profile_building,
      on_duty: form.profile_on_duty,
    }
    const existingProfile = profileMap.value[userId]
    if (existingProfile) {
      await updateStaffProfile(existingProfile.id, profileData)
    } else {
      await createStaffProfile(profileData)
    }
    ElMessage.success(editingId.value ? '已更新' : '员工已创建')
    formVisible.value = false
    loadData()
  } catch (e) {
    showAPIError(e, '保存失败')
  }
}

async function handleDisable(row) {
  await ElMessageBox.confirm(`确认禁用 ${row.last_name}${row.first_name} 的账号？`, '提示', { type: 'warning' })
  await updateUser(row.id, { is_active: false })
  ElMessage.success('已禁用')
  loadData()
}

onMounted(async () => {
  loadData()
  const [rData, bData] = await Promise.all([getRoles(), getBuildings()])
  roles.value = rData.results || rData
  buildings.value = bData.results || bData
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
