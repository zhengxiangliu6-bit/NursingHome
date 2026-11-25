<template>
  <div class="bed-map">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>床位状态图</span>
          <div class="legend">
            <span v-for="item in statusList" :key="item.value" class="legend-item">
              <span class="legend-dot" :style="{ background: item.color }"></span>{{ item.label }}
            </span>
          </div>
        </div>
      </template>

      <div v-if="loading" v-loading="loading" style="height: 200px;" />

      <div v-else-if="!buildings.length" class="empty-tip">
        <el-empty description="暂无床位数据" />
      </div>

      <template v-else>
        <!-- 楼栋选择 -->
        <el-tabs v-model="activeBuildingId" type="card">
          <el-tab-pane
            v-for="building in buildings"
            :key="building.id"
            :label="building.name"
            :name="building.id"
          />
        </el-tabs>

        <div v-if="activeBuilding">
          <!-- 楼层选择 -->
          <div class="floor-tabs">
            <el-button
              v-for="floorData in activeBuilding.floors"
              :key="floorData.floor"
              :type="activeFloor === floorData.floor ? 'primary' : 'default'"
              size="small"
              @click="activeFloor = floorData.floor"
            >
              {{ floorData.floor }}F
            </el-button>
          </div>

          <!-- 当前楼层房间/床位 -->
          <div v-if="activeFloorData" class="rooms-grid">
            <div
              v-for="room in activeFloorData.rooms"
              :key="room.room_id"
              class="room-card"
            >
              <div class="room-header">
                <span class="room-number">{{ room.room_number }}</span>
                <span class="room-type">{{ roomTypeMap[room.room_type] }}</span>
              </div>
              <div class="beds-row">
                <div
                  v-for="bed in room.beds"
                  :key="bed.bed_id"
                  class="bed-card"
                  :style="{ background: getStatusColor(bed.status) }"
                  @click="openBedDetail(bed, room)"
                >
                  <div class="bed-number">{{ bed.bed_number }}</div>
                  <div class="bed-resident" v-if="bed.resident_name">{{ bed.resident_name }}</div>
                  <div class="bed-status-label">{{ getStatusLabel(bed.status) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-card>

    <!-- 床位详情弹窗 -->
    <el-dialog v-model="detailVisible" title="床位详情" width="400px">
      <div v-if="selectedBed">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="床位号">
            {{ selectedRoom?.room_number }}-{{ selectedBed.bed_number }}
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :color="getStatusColor(selectedBed.status)" effect="light">
              {{ getStatusLabel(selectedBed.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="入住老人" v-if="selectedBed.resident_name">
            {{ selectedBed.resident_name }}
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 16px;">
          <div style="margin-bottom: 8px; font-weight: 500;">修改状态：</div>
          <el-button
            v-for="s in statusList"
            :key="s.value"
            size="small"
            :disabled="s.value === selectedBed.status"
            @click="changeStatus(s.value)"
          >
            {{ s.label }}
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getBedMap, updateBed } from '@/api/residents'
import { ElMessage } from 'element-plus'

const buildings = ref([])
const loading = ref(false)
const activeBuildingId = ref('')
const activeFloor = ref(null)
const detailVisible = ref(false)
const selectedBed = ref(null)
const selectedRoom = ref(null)

const statusList = [
  { value: 'available', label: '空闲', color: '#67C23A' },
  { value: 'occupied', label: '占用', color: '#F56C6C' },
  { value: 'leave', label: '请假', color: '#E6A23C' },
  { value: 'reserved', label: '预留', color: '#409EFF' },
  { value: 'maintenance', label: '维护', color: '#909399' },
  { value: 'cleaning', label: '清洁中', color: '#B88BD6' },
]

const roomTypeMap = { single: '单人间', double: '双人间', multi: '多人间' }

function getStatusColor(s) {
  return statusList.find(x => x.value === s)?.color || '#eee'
}
function getStatusLabel(s) {
  return statusList.find(x => x.value === s)?.label || s
}

const activeBuilding = computed(() => buildings.value.find(b => b.id === activeBuildingId.value))
const activeFloorData = computed(() => activeBuilding.value?.floors.find(f => f.floor === activeFloor.value))

async function loadMap() {
  loading.value = true
  try {
    const data = await getBedMap()
    buildings.value = data
    if (data.length) {
      activeBuildingId.value = data[0].id
      if (data[0].floors.length) activeFloor.value = data[0].floors[0].floor
    }
  } finally {
    loading.value = false
  }
}

function openBedDetail(bed, room) {
  selectedBed.value = { ...bed }
  selectedRoom.value = room
  detailVisible.value = true
}

async function changeStatus(newStatus) {
  try {
    await updateBed(selectedBed.value.bed_id, { status: newStatus })
    ElMessage.success('状态已更新')
    detailVisible.value = false
    await loadMap()
  } catch {
    ElMessage.error('更新失败')
  }
}

onMounted(loadMap)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.legend { display: flex; gap: 12px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 13px; }
.legend-dot { width: 12px; height: 12px; border-radius: 2px; display: inline-block; }
.floor-tabs { display: flex; gap: 8px; margin: 12px 0; flex-wrap: wrap; }
.rooms-grid { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 8px; }
.room-card { border: 1px solid #e4e7ed; border-radius: 8px; padding: 12px; min-width: 160px; }
.room-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.room-number { font-weight: 600; font-size: 15px; }
.room-type { font-size: 12px; color: #909399; }
.beds-row { display: flex; gap: 8px; flex-wrap: wrap; }
.bed-card {
  width: 72px; min-height: 72px; border-radius: 6px; padding: 6px; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #fff; transition: opacity 0.2s; text-align: center;
}
.bed-card:hover { opacity: 0.85; }
.bed-number { font-weight: 700; font-size: 14px; }
.bed-resident { font-size: 11px; margin-top: 2px; word-break: break-all; }
.bed-status-label { font-size: 11px; margin-top: 2px; }
.empty-tip { padding: 40px 0; }
</style>
