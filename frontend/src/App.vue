<template>
  <div class="app-page" :style="cssVariables">
  <main class="app-shell">
    <header class="window-bar">
      <div class="window-drag-region pywebview-drag-region"></div>
      <nav class="window-controls" aria-label="창 제어">
        <button type="button" aria-label="설정" title="설정" @click="openSettings">
          <img :src="settingsIcon" alt="" />
        </button>
        <button type="button" aria-label="최소화" title="최소화">
          <img :src="minimizeIcon" alt="" />
        </button>
        <button type="button" aria-label="최대화" title="최대화">
          <img :src="maximizeIcon" alt="" />
        </button>
        <button class="close-button" type="button" aria-label="닫기" title="닫기">
          <img :src="closeIcon" alt="" />
        </button>
      </nav>
    </header>

    <div class="workspace">
      <aside ref="sidebar" class="sidebar" :style="sidebarStyle">
      <section class="panel memo-panel">
        <div class="panel-heading">
          <button class="panel-label" type="button" :aria-expanded="isMemoOpen" @click="isMemoOpen = !isMemoOpen">메모</button>
          <span class="panel-actions">
            <template v-if="deleteMode === 'memo'">
              <button class="action-text-button" type="button" @click="requestDelete('memo')">삭제</button>
              <button class="action-text-button" type="button" @click="cancelDeleteMode">취소</button>
            </template>
            <template v-else>
              <button type="button" title="메모 추가" aria-label="메모 추가" @click="openDialog('memo')"><img :src="addIcon" alt="" /></button>
              <button type="button" title="메모 삭제 모드" aria-label="메모 삭제 모드" @click="startDeleteMode('memo')"><img :src="trashIcon" alt="" /></button>
              <button class="toggle-icon" type="button" :aria-label="isMemoOpen ? '메모 접기' : '메모 펼치기'" @click="isMemoOpen = !isMemoOpen">
              <img :src="isMemoOpen ? chevronDownIcon : chevronRightIcon" alt="" />
              </button>
            </template>
          </span>
        </div>
        <transition name="accordion">
          <div v-show="isMemoOpen" class="panel-list-scroll-shell">
            <ul ref="memoList" class="memo-list panel-list" @scroll="updateSidebarListScroll('memo')">
              <li v-for="memo in memos" :key="memo.id" class="memo-item">
                <div class="memo-item-row">
                <label v-if="deleteMode === 'memo'">
                  <input v-if="deleteMode === 'memo'" type="checkbox" :checked="memoSelectedIds.includes(memo.id)" @change="toggleMemoSelection(memo.id)" />
                </label>
                <button class="memo-title-button" type="button" :aria-expanded="expandedMemoIds.includes(memo.id)" @click="toggleMemoExpanded(memo.id)">
                  <span class="list-item-title">{{ memo.title }}</span>
                  <img :src="expandedMemoIds.includes(memo.id) ? chevronDownIcon : chevronRightIcon" alt="" />
                </button>
                </div>
                <transition name="memo-content">
                  <p v-show="expandedMemoIds.includes(memo.id)" class="memo-content">{{ memo.content || '내용이 없습니다.' }}</p>
                </transition>
              </li>
            </ul>
            <div v-if="memoScrollbarVisible" class="panel-retro-scrollbar" aria-hidden="true">
              <button type="button" tabindex="-1" @click="scrollSidebarList('memo', -48)"><img :src="chevronUpIcon" alt="" /></button>
              <div ref="memoListTrack" class="panel-retro-scroll-track" @click="jumpSidebarListScroll('memo', $event)">
                <div class="panel-retro-scroll-thumb" :style="memoThumbStyle"></div>
              </div>
              <button type="button" tabindex="-1" @click="scrollSidebarList('memo', 48)"><img :src="chevronDownIcon" alt="" /></button>
            </div>
          </div>
        </transition>
      </section>

      <section class="panel contact-panel">
        <div class="panel-heading">
          <button class="panel-label" type="button" :aria-expanded="isContactOpen" @click="isContactOpen = !isContactOpen">연락처</button>
          <span class="panel-actions">
            <template v-if="deleteMode === 'contact'">
              <button class="action-text-button" type="button" @click="requestDelete('contact')">삭제</button>
              <button class="action-text-button" type="button" @click="cancelDeleteMode">취소</button>
            </template>
            <template v-else>
              <button type="button" title="연락처 추가" aria-label="연락처 추가" @click="openDialog('contact')"><img :src="addIcon" alt="" /></button>
              <button type="button" title="연락처 삭제 모드" aria-label="연락처 삭제 모드" @click="startDeleteMode('contact')"><img :src="trashIcon" alt="" /></button>
              <button class="toggle-icon" type="button" :aria-label="isContactOpen ? '연락처 접기' : '연락처 펼치기'" @click="isContactOpen = !isContactOpen">
              <img :src="isContactOpen ? chevronDownIcon : chevronRightIcon" alt="" />
              </button>
            </template>
          </span>
        </div>
        <transition name="accordion">
          <div v-show="isContactOpen" class="panel-list-scroll-shell">
            <ul ref="contactList" class="contact-list panel-list" @scroll="updateSidebarListScroll('contact')">
              <li v-for="contact in contacts" :key="contact.id">
                <label>
                  <input v-if="deleteMode === 'contact'" type="checkbox" :checked="contactSelectedIds.includes(contact.id)" @change="toggleContactSelection(contact.id)" />
                  <span class="list-item-title">{{ contact.name }}</span>
                </label>
                <span>{{ contact.phone }}</span>
              </li>
            </ul>
            <div v-if="contactScrollbarVisible" class="panel-retro-scrollbar" aria-hidden="true">
              <button type="button" tabindex="-1" @click="scrollSidebarList('contact', -48)"><img :src="chevronUpIcon" alt="" /></button>
              <div ref="contactListTrack" class="panel-retro-scroll-track" @click="jumpSidebarListScroll('contact', $event)">
                <div class="panel-retro-scroll-thumb" :style="contactThumbStyle"></div>
              </div>
              <button type="button" tabindex="-1" @click="scrollSidebarList('contact', 48)"><img :src="chevronDownIcon" alt="" /></button>
            </div>
          </div>
        </transition>
      </section>
      <div class="sidebar-spacer" aria-hidden="true"></div>
      </aside>

      <section class="calendar-area">
      <header class="schedule-summary">
        <div class="selected-date">
          <button class="today-button" type="button" aria-label="오늘로 이동" title="오늘로 이동" @click="goToToday">
            <span :style="{ maskImage: `url(${calendarTodayIcon})` }"></span>
          </button>
          <div class="month-controls">
            <button type="button" aria-label="이전 달" @click="moveMonth(-1)"><img :src="chevronLeftIcon" alt="" /></button>
            <span>{{ month }}/{{ selectedDay }}</span>
            <button type="button" aria-label="다음 달" @click="moveMonth(1)"><img :src="chevronRightIcon" alt="" /></button>
          </div>
          <small>{{ selectedDateLabel }}</small>
        </div>
        <div class="schedule-scroll-shell">
        <ul ref="scheduleList" class="schedule-list" @scroll="updateScheduleScroll">
          <li v-for="schedule in selectedSchedules" :key="schedule.id" class="schedule-item">
            <span class="schedule-time">{{ schedule.time }}</span>
            <span class="schedule-title">{{ schedule.title }}</span>
            <button class="schedule-alert-button" type="button" :aria-label="schedule.alertEnabled ? '알림 끄기' : '알림 켜기'" @click="toggleScheduleAlert(schedule.id)">
              <span :class="{ 'is-active': schedule.alertEnabled }" :style="{ maskImage: `url(${schedule.alertEnabled ? bellIcon : bellOffIcon})` }"></span>
            </button>
            <button class="schedule-delete-button" type="button" aria-label="일정 삭제" @click="deleteSchedule(schedule.id)">
              <span :style="{ maskImage: `url(${trashIcon})` }"></span>
            </button>
          </li>
          <li class="schedule-add-item">
            <button type="button" @click="openDialog('schedule')"><img :src="addIcon" alt="" />일정 추가</button>
          </li>
        </ul>
        <div class="retro-scrollbar" :class="{ 'is-hidden': !scheduleScrollbarVisible }" aria-hidden="true">
          <button type="button" tabindex="-1" @click="scrollSchedule(-48)"><img :src="chevronUpIcon" alt="" /></button>
          <div ref="scheduleTrack" class="retro-scroll-track" @click="jumpScheduleScroll">
            <div class="retro-scroll-thumb" :style="scheduleThumbStyle"></div>
          </div>
          <button type="button" tabindex="-1" @click="scrollSchedule(48)"><img :src="chevronDownIcon" alt="" /></button>
        </div>
        </div>
      </header>

      <section class="calendar" aria-label="2026년 8월 달력">
        <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
        <button
          v-for="day in calendarDays"
          :key="day.key"
          class="calendar-day"
          :class="{
            'is-empty': !day.date,
            'is-selected': day.date === selectedDay,
            'has-schedule': day.hasSchedule
          }"
          type="button"
          :disabled="!day.date"
          @click="selectDay(day.date)"
        >
          <span v-if="day.date">{{ day.date }}</span>
          <i v-if="day.hasSchedule" aria-label="일정 있음"></i>
        </button>
      </section>
      </section>
    </div>
  </main>

  <div v-if="dialogType" class="dialog-backdrop" @mousedown.self="closeDialog">
    <form class="retro-dialog entry-dialog" @submit.prevent="submitDialog">
      <header>{{ dialogTitle }}</header>
      <label v-if="dialogType !== 'contact'">
        <span>{{ dialogType === 'memo' ? '메모 제목' : '일정 제목' }}</span>
        <input ref="dialogInput" v-model="dialogForm.title" required />
      </label>
      <label v-if="dialogType === 'memo'">
        <span>내용 <small>(선택)</small></span>
        <div class="memo-textarea-shell">
          <textarea ref="memoContentInput" v-model="dialogForm.content" rows="4" @scroll="updateMemoTextareaScroll"></textarea>
          <div class="retro-textarea-scrollbar" :class="{ 'is-hidden': !memoTextareaScrollbarVisible }" aria-hidden="true">
            <button type="button" tabindex="-1" @click="scrollMemoTextarea(-36)"><img :src="chevronUpIcon" alt="" /></button>
            <div ref="memoTextareaTrack" class="retro-textarea-track" @click="jumpMemoTextareaScroll">
              <div class="retro-textarea-thumb" :style="memoTextareaThumbStyle"></div>
            </div>
            <button type="button" tabindex="-1" @click="scrollMemoTextarea(36)"><img :src="chevronDownIcon" alt="" /></button>
          </div>
        </div>
      </label>
      <label v-if="dialogType === 'contact'">
        <span>이름</span>
        <input ref="dialogInput" v-model="dialogForm.name" required />
      </label>
      <label v-if="dialogType === 'contact'">
        <span>전화번호</span>
        <input v-model="dialogForm.phone" placeholder="010-0000-0000" />
      </label>
      <label v-if="dialogType === 'schedule'">
        <span>시간</span>
        <input v-model="dialogForm.time" type="time" required />
      </label>
      <div class="dialog-buttons">
        <button type="submit">확인</button>
        <button type="button" @click="closeDialog">취소</button>
      </div>
    </form>
  </div>

  <div v-if="confirmDeleteType" class="dialog-backdrop" @mousedown.self="closeDeleteConfirm">
    <section class="retro-dialog delete-confirm" role="dialog" aria-modal="true" aria-label="삭제 확인">
      <header>삭제 확인</header>
      <p>선택한 {{ confirmDeleteType === 'memo' ? '메모' : '연락처' }}를 삭제하시겠습니까?</p>
      <div class="dialog-buttons">
        <button type="button" @click="confirmDelete">삭제</button>
        <button type="button" @click="closeDeleteConfirm">취소</button>
      </div>
    </section>
  </div>

  <div v-if="isSettingsOpen" class="dialog-backdrop" @mousedown.self="closeSettings">
    <section class="retro-dialog settings-dialog" role="dialog" aria-modal="true" aria-label="설정">
      <header>설정</header>
      <section class="settings-section" aria-labelledby="accent-color-title">
        <div class="settings-section-heading">
          <div>
            <h2 id="accent-color-title">주조색</h2>
            <p>앱 전체에 적용할 기본 색상입니다.</p>
          </div>
          <span class="accent-color-preview" :style="{ backgroundColor: settingsAccentColor }" aria-hidden="true"></span>
        </div>
        <div class="settings-picker">
          <ChromePicker v-model="settingsAccentColor" :disable-alpha="true" @update:modelValue="updateAccentColor" />
        </div>
      </section>
      <div class="dialog-buttons">
        <button type="button" @click="closeSettings">닫기</button>
      </div>
    </section>
  </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'pinia'
import { useContactStore } from './stores/contact'
import { useMemoStore } from './stores/memo'
import { useReminderStore } from './stores/reminder'
import { useThemeStore } from './stores/theme'
import { ChromePicker } from 'vue-color'
import 'vue-color/style.css'
import settingsIcon from 'pixelarticons/svg/settings-cog.svg'
import minimizeIcon from 'pixelarticons/svg/minus.svg'
import maximizeIcon from 'pixelarticons/svg/expand.svg'
import closeIcon from 'pixelarticons/svg/close.svg'
import trashIcon from 'pixelarticons/svg/trash.svg'
import chevronDownIcon from 'pixelarticons/svg/chevron-down.svg'
import chevronRightIcon from 'pixelarticons/svg/chevron-right.svg'
import chevronLeftIcon from 'pixelarticons/svg/chevron-left.svg'
import addIcon from 'pixelarticons/svg/plus.svg'
import calendarTodayIcon from 'pixelarticons/svg/calendar-2.svg'
import chevronUpIcon from 'pixelarticons/svg/chevron-up.svg'
import bellIcon from 'pixelarticons/svg/bell.svg'
import bellOffIcon from 'pixelarticons/svg/bell-off.svg'


export default {
  name: 'App',
  components: {
    ChromePicker
  },
  data() {
    return {
      isMemoOpen: true,
      isContactOpen: true,
      expandedMemoIds: [],
      sidebarHeight: 0,
      resizeObserver: null,
      dialogType: null,
      isSettingsOpen: false,
      settingsAccentColor: '#ffdbd9',
      deleteMode: null,
      confirmDeleteType: null,
      dialogForm: { title: '', content: '', name: '', phone: '', time: '09:00' },
      settingsIcon,
      minimizeIcon,
      maximizeIcon,
      closeIcon,
      trashIcon,
      chevronDownIcon,
      chevronRightIcon,
      chevronLeftIcon,
      addIcon,
      calendarTodayIcon,
      chevronUpIcon,
      bellIcon,
      bellOffIcon,
      scheduleScrollTop: 0,
      scheduleScrollHeight: 0,
      scheduleClientHeight: 0,
      memoTextareaScrollTop: 0,
      memoTextareaScrollHeight: 0,
      memoTextareaClientHeight: 0,
      memoListScrollTop: 0,
      memoListScrollHeight: 0,
      memoListClientHeight: 0,
      contactListScrollTop: 0,
      contactListScrollHeight: 0,
      contactListClientHeight: 0,
      weekdays: ['일', '월', '화', '수', '목', '금', '토'],
    }
  },
  computed: {
    ...mapState(useReminderStore, ['year', 'month', 'selectedDay', 'schedules', 'selectedSchedules', 'selectedDateLabel']),
    ...mapState(useMemoStore, { memos: 'memos', memoSelectedIds: 'selectedIds' }),
    ...mapState(useContactStore, { contacts: 'contacts', contactSelectedIds: 'selectedIds' }),
    ...mapState(useThemeStore, ['accentColor', 'cssVariables']),
    dialogTitle() {
      return this.dialogType === 'memo' ? '메모 추가' : this.dialogType === 'contact' ? '연락처 추가' : '일정 추가'
    },
    scheduleScrollbarVisible() {
      return this.scheduleScrollHeight > this.scheduleClientHeight
    },
    scheduleThumbStyle() {
      if (!this.scheduleScrollbarVisible) return {}
      const thumbHeight = Math.max(18, (this.scheduleClientHeight / this.scheduleScrollHeight) * 100)
      const maxScrollTop = this.scheduleScrollHeight - this.scheduleClientHeight
      const top = (this.scheduleScrollTop / maxScrollTop) * (100 - thumbHeight)

      return { height: `${thumbHeight}%`, top: `${top}%` }
    },
    memoTextareaScrollbarVisible() {
      return this.memoTextareaScrollHeight > this.memoTextareaClientHeight
    },
    memoTextareaThumbStyle() {
      if (!this.memoTextareaScrollbarVisible) return {}
      const thumbHeight = Math.max(18, (this.memoTextareaClientHeight / this.memoTextareaScrollHeight) * 100)
      const maxScrollTop = this.memoTextareaScrollHeight - this.memoTextareaClientHeight
      const top = (this.memoTextareaScrollTop / maxScrollTop) * (100 - thumbHeight)

      return { height: `${thumbHeight}%`, top: `${top}%` }
    },
    memoScrollbarVisible() {
      return this.memoListScrollHeight > this.memoListClientHeight
    },
    memoThumbStyle() {
      return this.sidebarListThumbStyle('memo')
    },
    contactScrollbarVisible() {
      return this.contactListScrollHeight > this.contactListClientHeight
    },
    contactThumbStyle() {
      return this.sidebarListThumbStyle('contact')
    },
    sidebarStyle() {
      if (!this.sidebarHeight) {
        return {}
      }

      const headerHeight = 43
      const openHeight = Math.max(0, this.sidebarHeight - headerHeight * 2)
      let rows

      if (this.isMemoOpen && this.isContactOpen) {
        const halfHeight = Math.floor(openHeight / 2)
        rows = `${headerHeight + halfHeight}px ${headerHeight + openHeight - halfHeight}px 0px`
      } else if (this.isMemoOpen) {
        rows = `${this.sidebarHeight - headerHeight}px ${headerHeight}px 0px`
      } else if (this.isContactOpen) {
        rows = `${headerHeight}px ${this.sidebarHeight - headerHeight}px 0px`
      } else {
        rows = `${headerHeight}px ${headerHeight}px ${openHeight}px`
      }

      return { gridTemplateRows: rows }
    },
    calendarDays() {
      const firstDayOffset = new Date(this.year, this.month - 1, 1).getDay()
      const daysInMonth = new Date(this.year, this.month, 0).getDate()
      const totalCells = 42

      return Array.from({ length: totalCells }, (_, index) => {
        const date = index - firstDayOffset + 1
        const isCurrentMonth = date > 0 && date <= daysInMonth

        return {
          key: index,
          date: isCurrentMonth ? date : null,
          hasSchedule: isCurrentMonth && this.schedules.some((schedule) => (
            schedule.year === this.year && schedule.month === this.month && schedule.day === date
          ))
        }
      })
    }
  },
  methods: {
    ...mapActions(useReminderStore, ['selectDay', 'moveMonth', 'goToToday', 'addSchedule', 'toggleScheduleAlert', 'deleteSchedule', 'loadSchedules']),
    ...mapActions(useThemeStore, ['setAccentColor', 'loadSettings']),
    ...mapActions(useMemoStore, { addMemo: 'addMemo', loadMemos: 'loadMemos', toggleMemoSelection: 'toggleSelection', deleteSelectedMemos: 'deleteSelected', clearMemoSelection: 'clearSelection' }),
    ...mapActions(useContactStore, { addContact: 'addContact', loadContacts: 'loadContacts', toggleContactSelection: 'toggleSelection', deleteSelectedContacts: 'deleteSelected', clearContactSelection: 'clearSelection' }),
    startDeleteMode(type) {
      this.deleteMode = type
      if (type === 'memo') this.clearMemoSelection()
      if (type === 'contact') this.clearContactSelection()
    },
    cancelDeleteMode() {
      this.clearMemoSelection()
      this.clearContactSelection()
      this.deleteMode = null
    },
    requestDelete(type) {
      const selectedIds = type === 'memo' ? this.memoSelectedIds : this.contactSelectedIds
      if (selectedIds.length) this.confirmDeleteType = type
    },
    closeDeleteConfirm() {
      this.confirmDeleteType = null
    },
    async confirmDelete() {
      if (this.confirmDeleteType === 'memo') await this.deleteSelectedMemos()
      if (this.confirmDeleteType === 'contact') await this.deleteSelectedContacts()
      this.confirmDeleteType = null
      this.deleteMode = null
    },
    openDialog(type) {
      this.dialogType = type
      this.dialogForm = { title: '', content: '', name: '', phone: '', time: '09:00' }
      this.$nextTick(() => this.$refs.dialogInput.focus())
    },
    closeDialog() {
      this.dialogType = null
    },
    openSettings() {
      this.settingsAccentColor = this.accentColor
      this.isSettingsOpen = true
    },
    closeSettings() {
      this.isSettingsOpen = false
    },
    async updateAccentColor(color) {
      const normalized = color.replace('#', '')
      const expanded = normalized.length === 3
        ? normalized.split('').map((character) => `${character}${character}`).join('')
        : normalized

      if (!/^[0-9a-fA-F]{6}$/.test(expanded)) return

      const hex = `#${expanded.toLowerCase()}`
      this.settingsAccentColor = hex
      await this.setAccentColor(hex)
    },
    async submitDialog() {
      if (this.dialogType === 'memo') await this.addMemo(this.dialogForm.title, this.dialogForm.content)
      if (this.dialogType === 'contact') await this.addContact(this.dialogForm.name, this.dialogForm.phone)
      if (this.dialogType === 'schedule') await this.addSchedule(this.dialogForm.title, this.dialogForm.time)
      this.closeDialog()
    },
    async initializeData() {
      await Promise.all([this.loadMemos(), this.loadContacts(), this.loadSchedules(), this.loadSettings()])
    },
    toggleMemoExpanded(id) {
      this.expandedMemoIds = this.expandedMemoIds.includes(id)
        ? this.expandedMemoIds.filter((memoId) => memoId !== id)
        : [...this.expandedMemoIds, id]
    },
    updateSidebarHeight() {
      this.sidebarHeight = Math.max(0, this.$refs.sidebar.clientHeight - 4)
      this.$nextTick(() => {
        this.updateSidebarListScroll('memo')
        this.updateSidebarListScroll('contact')
      })
    },
    updateScheduleScroll() {
      const list = this.$refs.scheduleList
      if (!list) return
      this.scheduleScrollTop = list.scrollTop
      this.scheduleScrollHeight = list.scrollHeight
      this.scheduleClientHeight = list.clientHeight
    },
    updateMemoTextareaScroll() {
      const textarea = this.$refs.memoContentInput
      if (!textarea) return
      this.memoTextareaScrollTop = textarea.scrollTop
      this.memoTextareaScrollHeight = textarea.scrollHeight
      this.memoTextareaClientHeight = textarea.clientHeight
    },
    updateSidebarListScroll(type) {
      const list = this.$refs[`${type}List`]
      if (!list) return
      this[`${type}ListScrollTop`] = list.scrollTop
      this[`${type}ListScrollHeight`] = list.scrollHeight
      this[`${type}ListClientHeight`] = list.clientHeight
    },
    sidebarListThumbStyle(type) {
      const scrollHeight = this[`${type}ListScrollHeight`]
      const clientHeight = this[`${type}ListClientHeight`]
      const scrollTop = this[`${type}ListScrollTop`]
      if (scrollHeight <= clientHeight) return {}
      const thumbHeight = Math.max(18, (clientHeight / scrollHeight) * 100)
      const maxScrollTop = scrollHeight - clientHeight
      const top = (scrollTop / maxScrollTop) * (100 - thumbHeight)

      return { height: `${thumbHeight}%`, top: `${top}%` }
    },
    scrollSchedule(offset) {
      this.$refs.scheduleList.scrollBy({ top: offset, behavior: 'smooth' })
    },
    jumpScheduleScroll(event) {
      const track = this.$refs.scheduleTrack
      const list = this.$refs.scheduleList
      const ratio = (event.clientY - track.getBoundingClientRect().top) / track.clientHeight
      list.scrollTop = ratio * (list.scrollHeight - list.clientHeight)
    },
    scrollMemoTextarea(offset) {
      this.$refs.memoContentInput.scrollBy({ top: offset, behavior: 'smooth' })
    },
    jumpMemoTextareaScroll(event) {
      const track = this.$refs.memoTextareaTrack
      const textarea = this.$refs.memoContentInput
      const ratio = (event.clientY - track.getBoundingClientRect().top) / track.clientHeight
      textarea.scrollTop = ratio * (textarea.scrollHeight - textarea.clientHeight)
    },
    scrollSidebarList(type, offset) {
      this.$refs[`${type}List`].scrollBy({ top: offset, behavior: 'smooth' })
    },
    jumpSidebarListScroll(type, event) {
      const track = this.$refs[`${type}ListTrack`]
      const list = this.$refs[`${type}List`]
      const ratio = (event.clientY - track.getBoundingClientRect().top) / track.clientHeight
      list.scrollTop = ratio * (list.scrollHeight - list.clientHeight)
    }
  },
  mounted() {
    this.updateSidebarHeight()
    this.resizeObserver = new ResizeObserver(this.updateSidebarHeight)
    this.resizeObserver.observe(this.$refs.sidebar)
    this.initializeData()
    this.$nextTick(this.updateScheduleScroll)
  },
  updated() {
    this.$nextTick(this.updateScheduleScroll)
    this.$nextTick(this.updateMemoTextareaScroll)
    this.$nextTick(() => {
      this.updateSidebarListScroll('memo')
      this.updateSidebarListScroll('contact')
    })
  },
  beforeUnmount() {
    this.resizeObserver.disconnect()
  }
}
</script>

<style src="./assets/styles/App.css"></style>

