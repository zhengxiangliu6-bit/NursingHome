<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>房间管理</span>
          <el-button type="primary" @click="openCreate">添加房间</el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" style="margin-bottom: 12px;">
        <el-form-item label="楼栋">
          <el-select v-model="filterBuilding" clearable placeholder="全部" @change="loadData" style="width:130px">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterType" clearable placeholder="全部" @change="loadData" style="width:100px">
            <el-option label="单人间" value="single" />
            <el-option label="双人间" value="double" />
            <el-option label="多人间" value="multi" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="rooms" v-loading="loading" stripe row-key="id">
        <el-table-column prop="room_number" label="房间号" width="100" />
        <el-table-column prop="building_name" label="楼栋" width="120" />
        <el-table-column prop="floor" label="楼层" width="70" />
        <el-table-column prop="room_type" label="类型" width="90">
          <template #default="{ row }">
            {{ { single: '单人间', double: '双人间', multi: '多人间' }[row.room_type] }}
          </template>
        </el-table-column>
        <el-table-column label="床位" min-width="220">
          <template #default="{ row }">
            <div class="bed-inline">
              <el-tag
                v-for="bed in row.beds"
                :key="bed.id"
                :type="bedTagType(bed.status)"
                size="small"
                style="margin-right: 4px; margin-bottom: 2px; cursor:pointer;"
                @click="openBedEdit(bed, row)"
              >
                {{ bed.bed_number }}: {{ bedStatusLabel(bed.status) }}
              </el-tag>
              <el-button size="small" :icon="Plus" circle @click="openAddBed(row)" title="添加床位" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="occupancy" label="已入住" width="80" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑房间弹窗 -->
    <el-dialog v-model="roomFormVisible" :title="editingId ? '编辑房间' : '添加房间'" width="500px" @closed="roomFormRef?.clearValidate()">
      <el-form :model="form" label-width="80px" ref="roomFormRef" :rules="roomRules">
        <el-form-item label="房间号" prop="room_number"><el-input v-model="form.room_number" /></el-form-item>
        <el-form-item label="楼栋" prop="building">
          <el-select v-model="form.building" placeholder="请选择" style="width:100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="楼层"><el-input-number v-model="form.floor" :min="1" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.room_type" style="width:100%">
            <el-option label="单人间" value="single" />
            <el-option label="双人间" value="double" />
            <el-option label="多人间" value="multi" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量"><el-input-number v-model="form.capacity" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roomFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRoomSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑床位弹窗 -->
    <el-dialog v-model="bedFormVisible" :title="editingBedId ? '编辑床位' : '添加床位'" width="400px" @closed="bedFormRef?.clearValidate()">
      <el-form :model="bedForm" label-width="80px" ref="bedFormRef" :rules="bedRules">
        <el-form-item label="床位号" prop="bed_number"><el-input v-model="bedForm.bed_number" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="bedForm.status" style="width:100%">
            <el-option label="空闲" value="available" />
            <el-option label="已占用" value="occupied" />
            <el-option label="请假" value="leave" />
            <el-option label="预留" value="reserved" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="清洁中" value="cleaning" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bedFormVisible = false">取消</el-button>
        <el-button v-if="editingBedId" type="danger" @click="handleBedDelete">删除床位</el-button>
        <el-button type="primary" @click="handleBedSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getRooms, createRoom, updateRoom, deleteRoom, createBed, updateBed, deleteBed } from '@/api/residents'
import { getBuildings } from '@/api/campus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showAPIError } from '@/utils/errorHelper'
import { Plus } from '@element-plus/icons-vue'

const rooms = ref([])
const buildings = ref([])
const loading = ref(false)
const filterBuilding = ref('')
const filterType = ref('')

const roomFormRef = ref(null)
const roomRules = {
  room_number: [{ required: true, message: '请输入房间号', trigger: 'blur' }],
  building: [{ required: true, message: '请选择楼栋', trigger: 'change' }],
}

const roomFormVisible = ref(false)
const editingId = ref(null)
const form = reactive({ room_number: '', building: '', floor: 1, room_type: 'double', capacity: 2 })

const bedFormRef = ref(null)
const bedRules = {
  bed_number: [{ required: true, message: '请输入床位号', trigger: 'blur' }],
}

const bedFormVisible = ref(false)
const editingBedId = ref(null)
const currentRoomId = ref(null)
const bedForm = reactive({ bed_number: '', status: 'available' })

const bedStatusMap = { available: '空闲', occupied: '已占用', leave: '请假', reserved: '预留', maintenance: '维护', cleaning: '清洁中' }
function bedStatusLabel(s) { return bedStatusMap[s] || s }
function bedTagType(s) {
  return { available: 'success', occupied: 'danger', leave: 'warning', reserved: '', maintenance: 'info', cleaning: 'warning' }[s] || ''
}

async function loadData() {
  loading.value = true
  try {
    const params = {}
    if (filterBuilding.value) params.building = filterBuilding.value
    if (filterType.value) params.room_type = filterType.value
    const data = await getRooms(params)
    rooms.value = data.results || data
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { room_number: '', building: '', floor: 1, room_type: 'double', capacity: 2 })
  roomFormVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    room_number: row.room_number, building: row.building,
    floor: row.floor, room_type: row.room_type, capacity: row.capacity,
  })
  roomFormVisible.value = true
}

async function handleRoomSave() {
  try {
    await roomFormRef.value.validate()
  } catch { return }
  try {
    if (editingId.value) {
      await updateRoom(editingId.value, form)
      ElMessage.success('房间已更新')
    } else {
      await createRoom(form)
      ElMessage.success('房间添加成功')
    }
    roomFormVisible.value = false
    loadData()
  } catch (e) { showAPIError(e, '保存失败') }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除房间 ${row.room_number}？此操作不可恢复。`, '提示', { type: 'warning' })
  await deleteRoom(row.id)
  ElMessage.success('已删除')
  loadData()
}

function openAddBed(room) {
  editingBedId.value = null
  currentRoomId.value = room.id
  Object.assign(bedForm, { bed_number: '', status: 'available' })
  bedFormVisible.value = true
}

function openBedEdit(bed, room) {
  editingBedId.value = bed.id
  currentRoomId.value = room.id
  Object.assign(bedForm, { bed_number: bed.bed_number, status: bed.status })
  bedFormVisible.value = true
}

async function handleBedSave() {
  try {
    await bedFormRef.value.validate()
  } catch { return }
  try {
    if (editingBedId.value) {
      await updateBed(editingBedId.value, bedForm)
      ElMessage.success('床位已更新')
    } else {
      await createBed({ ...bedForm, room: currentRoomId.value })
      ElMessage.success('床位已添加')
    }
    bedFormVisible.value = false
    loadData()
  } catch (e) { showAPIError(e, '保存失败') }
}

async function handleBedDelete() {
  await ElMessageBox.confirm('确认删除此床位？', '提示', { type: 'warning' })
  await deleteBed(editingBedId.value)
  ElMessage.success('已删除')
  bedFormVisible.value = false
  loadData()
}

onMounted(async () => {
  loadData()
  const data = await getBuildings()
  buildings.value = data.results || data
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.bed-inline { display: flex; flex-wrap: wrap; align-items: center; gap: 2px; }
</style>
