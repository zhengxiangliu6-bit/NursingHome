<template>
  <div class="sidebar-container">
    <div class="logo">
      <span v-if="!collapsed">智慧养老</span>
      <span v-else>养</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><DataBoard /></el-icon>
        <template #title>综合看板</template>
      </el-menu-item>

      <el-sub-menu index="call-response">
        <template #title>
          <el-icon><Phone /></el-icon>
          <span>呼叫响应</span>
        </template>
        <el-menu-item index="/call-response">呼叫监控</el-menu-item>
        <el-menu-item index="/call-response/history">呼叫历史</el-menu-item>
        <el-menu-item index="/call-response/devices">呼叫设备</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="smart-detection">
        <template #title>
          <el-icon><FirstAidKit /></el-icon>
          <span>智能检测</span>
        </template>
        <el-menu-item index="/smart-detection/vitals">体征监控</el-menu-item>
        <el-menu-item index="/smart-detection/fall">跌倒预警</el-menu-item>
        <el-menu-item index="/smart-detection/health">健康检查</el-menu-item>
        <el-menu-item index="/smart-detection/position">定位地图</el-menu-item>
        <el-menu-item index="/smart-detection/alert-center">告警中心</el-menu-item>
        <el-menu-item index="/smart-detection/rules">告警规则</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="patrol">
        <template #title>
          <el-icon><MapLocation /></el-icon>
          <span>巡更管理</span>
        </template>
        <el-menu-item index="/patrol/schedule">巡更排班</el-menu-item>
        <el-menu-item index="/patrol/monitor">实时巡更</el-menu-item>
        <el-menu-item index="/patrol/checkpoints">巡更点管理</el-menu-item>
        <el-menu-item index="/patrol/records">巡更记录</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="broadcasting">
        <template #title>
          <el-icon><Microphone /></el-icon>
          <span>公共广播</span>
        </template>
        <el-menu-item index="/broadcasting/control">广播控制</el-menu-item>
        <el-menu-item index="/broadcasting/schedule">定时广播</el-menu-item>
        <el-menu-item index="/broadcasting/logs">广播日志</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="campus">
        <template #title>
          <el-icon><OfficeBuilding /></el-icon>
          <span>院区管理</span>
        </template>
        <el-menu-item index="/campus/devices">设备管理</el-menu-item>
        <el-menu-item index="/campus/buildings">楼栋管理</el-menu-item>
        <el-menu-item index="/campus/notices">信息发布</el-menu-item>
        <el-menu-item index="/campus/assessment">护理评估</el-menu-item>
        <el-menu-item index="/campus/staff">员工档案</el-menu-item>
        <el-menu-item index="/campus/schedule">排班管理</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="residents">
        <template #title>
          <el-icon><User /></el-icon>
          <span>老人管理</span>
        </template>
        <el-menu-item index="/residents">老人列表</el-menu-item>
        <el-menu-item index="/residents/rooms">房间管理</el-menu-item>
        <el-menu-item index="/residents/bed-map">床位状态图</el-menu-item>
        <el-menu-item index="/residents/admission">入住流程</el-menu-item>
        <el-menu-item index="/residents/bed-transfer">床位调换</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()
const collapsed = computed(() => appStore.sidebarCollapsed)
const activeMenu = computed(() => route.path)
</script>

<style lang="scss" scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background: #263445;
  white-space: nowrap;
  overflow: hidden;
}

.el-menu {
  border-right: none;
  flex: 1;
}
</style>
