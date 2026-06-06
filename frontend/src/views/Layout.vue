<template>
  <el-container class="layout-container">
    <el-aside width="220px">
      <div class="logo">
        <el-icon :size="24"><Medical /></el-icon>
        <span>康复随访系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin()" index="/templates">
          <el-icon><Document /></el-icon>
          <span>模板管理</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin() || userStore.isUser()" index="/upload">
          <el-icon><Upload /></el-icon>
          <span>批量导入</span>
        </el-menu-item>
        <el-menu-item index="/records">
          <el-icon><List /></el-icon>
          <span>随访记录</span>
        </el-menu-item>
        <el-menu-item index="/plans">
          <el-icon><Calendar /></el-icon>
          <span>回访计划</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin() || userStore.isAuditor()" index="/audit">
          <el-icon><View /></el-icon>
          <span>审计日志</span>
        </el-menu-item>
        <el-menu-item index="/alerts">
          <el-icon><Bell /></el-icon>
          <span>异常提醒</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-left">
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.user?.full_name || userStore.user?.username }}
              <span class="role-tag">({{ roleText }})</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '数据概览',
    '/templates': '模板管理',
    '/upload': '批量导入',
    '/records': '随访记录',
    '/plans': '回访计划',
    '/audit': '审计日志',
    '/alerts': '异常提醒'
  }
  return titles[route.path] || ''
})

const roleText = computed(() => {
  const roles = {
    'admin': '管理员',
    'user': '普通用户',
    'auditor': '审计员'
  }
  return roles[userStore.user?.role] || ''
})

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  background: #2b2f3a;
}

.logo .el-icon {
  margin-right: 8px;
}

.el-menu {
  border-right: none;
}

.el-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-info .el-icon {
  margin-right: 5px;
}

.role-tag {
  color: #909399;
  font-size: 12px;
  margin-left: 5px;
}

.el-main {
  background: #f0f2f5;
  padding: 20px;
}
</style>
