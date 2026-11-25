<template>
  <div class="staff-schedule">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排班管理</span>
          <div class="header-controls">
            <el-button @click="prevWeek">&#8249; 上周</el-button>
            <span class="week-range">{{ weekRange }}</span>
            <el-button @click="nextWeek">下周 &#8250;</el-button>
            <el-button type="primary" @click="openCreate">新增排班</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" style="margin-bottom: 12px;">
        <el-form-item label="楼栋">
          <el-select v-model="filterBuilding" clearable placeholder="全部" @change="loadData" style="width:120px">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filterRole" clearable placeholder="全部" @change="loadData" style="width:120px">
            <el-option v-for="r in roles" :key="r.id" :label="r.display_name || r.name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 周视图表格 -->
      <div v-loading="loading" class="schedule-table-wrap">
        <el-table :data="staffRows" border size="small">
          <el-table-column label="员工" width="100" fixed="left">
            <template #default="{ row }">{{ row.name }}</template>
          </el-table-column>
          <el-table-column
            v-for="day in weekDays"
            :key="day.date"
            :label="`${day.label}\n${day.date.slice(5)}`"
            min-width="100"
          >
            <template #header>
              <div style="text-align:center; line-height:1.4">
                <div>{{ day.label }}</div>
                <div style="font-size:11px;color:#909399">{{ day.date.slice(5) }}</div>
              </div>
            </template>
            <template #default="{ row }">
              <div class="cell-content" @click="openCellEdit(row, day)">
                <div v-if="getCellSchedules(row.id, day.date).length">
                  <el-tag
                    v-for="s in getCellSchedules(row.id, day.date)"
                    :key="s.id"
                    :type="s.is_on_leave ? 'danger' : shiftTagType(s.shift)"
                    size="small"
                    style="display:block; margin-bottom:2px; cursor:pointer"
                    closable
                    @close.stop="handleDelete(s)"
                  >
                    {{ s.is_on_leave ? '请假' : shiftShortLabel(s.shift) }}
                  </el-tag>
                </div>
                <div v-else class="empty-cell">+</div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="formVisible" title="排班设置" width="400px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="员工">
          <el-select v-model="form.staff" style="width:100%" filterable>
            <el-option v-for="s in allStaff" :key="s.id" :label="`${s.last_name}${s.first_name}`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="班次">
          <el-select v-model="form.shift" style="width:100%">
            <el-option label="早班 06:00-14:00" value="morning" />
            <el-option label="午班 14:00-22:00" value="afternoon" />
            <el-option label="夜班 22:00-06:00" value="night" />
          </el-select>
        </el-form-item>
        <el-form-item label="楼栋">
          <el-select v-model="form.building" clearable style="width:100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="请假">
          <el-switch v-model="form.is_on_leave" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" />
        </el-form-item>
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
import { getSchedules, createSchedule, deleteSchedule, getRoles } from '@/api/auth'
import { getUsers } from '@/api/auth'
import { getBuildings } from '@/api/campus'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const schedules = ref([])
const allStaff = ref([])
const roles = ref([])
const buildings = ref([])
const loading = ref(false)
const weekStart = ref(dayjs().startOf('week').add(1, 'day')) // Monday
const filterBuilding = ref('')
const filterRole = ref('')
const formVisible = ref(false)
const form = reactive({ staff: '', date: '', shift: 'morning', building: null, is_on_leave: false, notes: '' })

const weekDays = computed(() => {
  const days = []
  const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  for (let i = 0; i < 7; i++) {
    const d = weekStart.value.add(i, 'day')
    days.push({ date: d.format('YYYY-MM-DD'), label: labels[i] })
  }
  return days
})

const weekRange = computed(() => {
  const end = weekStart.value.add(6, 'day')
  return `${weekStart.value.format('MM/DD')} - ${end.format('MM/DD')}`
})

const staffRows = computed(() => {
  return allStaff.value
    .filter(s => !filterRole.value || s.role === filterRole.value)
    .map(s => ({ id: s.id, name: `${s.last_name}${s.first_name}` || s.username }))
})

function getCellSchedules(staffId, date) {
  return schedules.value.filter(s => s.staff === staffId && s.date === date)
}

function shiftTagType(shift) {
  return { morning: '', afternoon: 'warning', night: 'info' }[shift] || ''
}
function shiftShortLabel(shift) {
  return { morning: '早班', afternoon: '午班', night: '夜班' }[shift] || shift
}

function prevWeek() { weekStart.value = weekStart.value.subtract(7, 'day'); loadData() }
function nextWeek() { weekStart.value = weekStart.value.add(7, 'day'); loadData() }

async function loadData() {
  loading.value = true
  try {
    const params = {
      date_from: weekDays.value[0].date,
      date_to: weekDays.value[6].date,
    }
    if (filterBuilding.value) params.building = filterBuilding.value
    const data = await getSchedules(params)
    schedules.value = data.results || data
  } finally { loading.value = false }
}

function openCreate() {
  Object.assign(form, { staff: '', date: weekDays.value[0].date, shift: 'morning', building: null, is_on_leave: false, notes: '' })
  formVisible.value = true
}

function openCellEdit(row, day) {
  Object.assign(form, { staff: row.id, date: day.date, shift: 'morning', building: null, is_on_leave: false, notes: '' })
  formVisible.value = true
}

async function handleSave() {
  try {
    await createSchedule(form)
    ElMessage.success('排班已保存')
    formVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.non_field_errors?.[0] || '保存失败')
  }
}

async function handleDelete(s) {
  await ElMessageBox.confirm('确认删除此排班？', '提示', { type: 'warning' })
  await deleteSchedule(s.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(async () => {
  const [sData, rData, bData] = await Promise.all([getUsers(), getRoles(), getBuildings()])
  allStaff.value = (sData.results || sData).filter(u => u.role_name !== '家属')
  roles.value = rData.results || rData
  buildings.value = bData.results || bData
  loadData()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.header-controls { display: flex; align-items: center; gap: 8px; }
.week-range { font-weight: 500; min-width: 110px; text-align: center; }
.schedule-table-wrap { overflow-x: auto; }
.cell-content { min-height: 36px; cursor: pointer; padding: 2px; }
.empty-cell { color: #c0c4cc; font-size: 18px; text-align: center; line-height: 32px; }
</style>
