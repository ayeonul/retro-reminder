<template>
  <div class="app-page" :class="{ 'use-pixel-font': usePixelFont }" :style="cssVariables">
  <div class="window-resize-handle resize-top" @pointerdown.prevent="startWindowResize('top', $event)"></div>
  <div class="window-resize-handle resize-right" @pointerdown.prevent="startWindowResize('right', $event)"></div>
  <div class="window-resize-handle resize-bottom" @pointerdown.prevent="startWindowResize('bottom', $event)"></div>
  <div class="window-resize-handle resize-left" @pointerdown.prevent="startWindowResize('left', $event)"></div>
  <div class="window-resize-handle resize-bottom-right" @pointerdown.prevent="startWindowResize('bottom-right', $event)"></div>
  <main class="app-shell">
    <header class="window-bar">
      <div class="window-drag-region pywebview-drag-region"></div>
      <nav class="window-controls" aria-label="창 제어">
        <button type="button" aria-label="설정" title="설정" @click="openSettings">
          <img :src="settingsIcon" alt="" />
        </button>
        <button type="button" aria-label="최소화" title="최소화" @click="minimizeWindow">
          <img :src="minimizeIcon" alt="" />
        </button>
        <button class="close-button" type="button" aria-label="닫기" title="닫기" @click="closeWindow">
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
            <span class="selected-month-day">{{ month }}/{{ selectedDay }}</span>
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
            'is-adjacent': !day.isCurrentMonth,
            'is-selected': day.year === year && day.month === month && day.date === selectedDay,
            'has-schedule': day.hasSchedule
          }"
          type="button"
          @click="selectCalendarDay(day)"
        >
          <span>{{ day.date }}</span>
          <i v-if="day.hasSchedule" aria-label="일정 있음"></i>
        </button>
      </section>
      </section>
    </div>
  </main>

  <div v-if="dialogType" class="dialog-backdrop" @mousedown.self="closeDialog">
    <form class="retro-dialog entry-dialog" @submit.prevent="submitDialog">
      <header><span>{{ dialogTitle }}</span><button class="dialog-close" type="button" aria-label="닫기" @click="closeDialog"><img :src="closeIcon" alt="" /></button></header>
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
        <input v-model="dialogForm.phone" placeholder="010-0000-0000" @input="sanitizePhone" />
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
      <header><span>삭제 확인</span><button class="dialog-close" type="button" aria-label="닫기" @click="closeDeleteConfirm"><img :src="closeIcon" alt="" /></button></header>
      <p>선택한 {{ confirmDeleteType === 'memo' ? '메모' : '연락처' }}를 삭제하시겠습니까?</p>
      <div class="dialog-buttons">
        <button type="button" @click="confirmDelete">삭제</button>
        <button type="button" @click="closeDeleteConfirm">취소</button>
      </div>
    </section>
  </div>

  <div v-if="isSettingsOpen" class="dialog-backdrop" @mousedown.self="closeSettings">
    <section class="retro-dialog settings-dialog" role="dialog" aria-modal="true" aria-label="설정">
      <header><span>설정</span><button class="dialog-close" type="button" aria-label="닫기" @click="closeSettings"><img :src="closeIcon" alt="" /></button></header>
      <section class="settings-section" aria-labelledby="accent-color-title">
        <div class="settings-section-heading">
          <div>
            <h2 id="accent-color-title">테마 설정</h2>
            <label class="pixel-font-option">
              <span>픽셀 폰트 사용</span>
              <input type="checkbox" :checked="usePixelFont" @change="setUsePixelFont($event.target.checked)" />
              </label>
              <p>앱 전체에 적용할 기본 색상입니다.</p>
              <p class="theme-restart-hint">아이콘 색상은 프로그램을 다시 실행하면 적용됩니다.</p>
            </div>
        </div>
        <div class="settings-picker">
          <ChromePicker v-model="settingsAccentColor" :disable-alpha="true" @update:modelValue="updateAccentColor" />
        </div>
      </section>
      <section class="settings-section backup-section" aria-labelledby="backup-title">
        <div class="settings-section-heading">
          <div>
            <h2 id="backup-title">데이터 백업</h2>
            <p>메모, 연락처, 일정 및 설정을 파일로 보관하거나 복원합니다.</p>
          </div>
        </div>
        <div class="backup-actions">
          <button type="button" @click="exportBackup">데이터 내보내기</button>
          <button type="button" @click="openBackupFilePicker">데이터 불러오기</button>
          <input ref="backupFileInput" type="file" accept=".db,application/vnd.sqlite3,application/octet-stream" @change="selectBackupFile" />
        </div>
      </section>
      <button class="license-link" type="button" @click="openLicenses">오픈소스 라이선스</button>
      <div class="dialog-buttons">
        <button type="button" @click="closeSettings">닫기</button>
      </div>
    </section>
  </div>

  <div v-if="isLicenseOpen" class="dialog-backdrop" @mousedown.self="closeLicenses">
    <section class="retro-dialog licenses-dialog" role="dialog" aria-modal="true" aria-label="오픈소스 라이선스">
        <header><span>오픈소스 라이선스</span><button class="dialog-close" type="button" aria-label="닫기" @click="closeLicenses"><img :src="closeIcon" alt="" /></button></header>
        <p class="license-intro">이 앱에서 사용하는 오픈소스 및 글꼴입니다.</p>
        <div class="license-scroll-shell">
          <div ref="licenseList" class="license-list" @scroll="updateLicenseScroll">
            <section v-for="group in licenseGroups" :key="group.name">
              <h2>{{ group.name }}</h2>
              <div v-for="license in group.items" :key="license.name" class="license-item">
                <span>{{ license.name }}</span>
                <small>{{ license.license }}<template v-if="license.creator"> · 제작자: {{ license.creator }}</template></small>
              </div>
            </section>
          </div>
          <div class="retro-scrollbar" :class="{ 'is-hidden': !licenseScrollbarVisible }" aria-hidden="true">
            <button type="button" tabindex="-1" @click="scrollLicenses(-48)"><img :src="chevronUpIcon" alt="" /></button>
            <div ref="licenseTrack" class="retro-scroll-track" @click="jumpLicenseScroll($event)">
              <div class="retro-scroll-thumb" :style="licenseThumbStyle"></div>
            </div>
            <button type="button" tabindex="-1" @click="scrollLicenses(48)"><img :src="chevronDownIcon" alt="" /></button>
          </div>
        </div>
    </section>
  </div>

  <div v-if="backupImportFile" class="dialog-backdrop" @mousedown.self="cancelBackupImport">
    <section class="retro-dialog delete-confirm" role="dialog" aria-modal="true" aria-label="데이터 불러오기 확인">
      <header><span>데이터 불러오기</span><button class="dialog-close" type="button" aria-label="닫기" @click="cancelBackupImport"><img :src="closeIcon" alt="" /></button></header>
      <p><strong>{{ backupImportFile.name }}</strong> 파일로 현재 데이터를 교체하시겠습니까?</p>
      <div class="dialog-buttons">
        <button type="button" @click="confirmBackupImport">불러오기</button>
        <button type="button" @click="cancelBackupImport">취소</button>
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
import apiClient from './api/client'
import { ChromePicker } from 'vue-color'
import 'vue-color/style.css'
import settingsIcon from 'pixelarticons/svg/settings-cog.svg'
import minimizeIcon from 'pixelarticons/svg/minus.svg'
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
        windowResize: null,
        resizeRequestFrame: null,
        pendingWindowResize: null,
        licenseScrollTop: 0,
        licenseScrollHeight: 0,
        licenseClientHeight: 0,
        todayKey: '',
        dateChangeTimer: null,
      dialogType: null,
      isSettingsOpen: false,
      isLicenseOpen: false,
      settingsAccentColor: '#ffdbd9',
      backupImportFile: null,
      licenseGroups: [
        {
          name: '프론트엔드',
          items: [
            { name: 'Vue', license: 'MIT License' },
            { name: 'Pinia', license: 'MIT License' },
            { name: 'Axios', license: 'MIT License' },
            { name: 'Vue Color', license: 'MIT License' },
            { name: 'Pixelarticons', license: 'MIT License' },
            { name: 'core-js', license: 'MIT License' }
          ]
        },
        {
          name: '백엔드',
          items: [
            { name: 'FastAPI', license: 'MIT License' },
            { name: 'Uvicorn', license: 'BSD 3-Clause License' },
            { name: 'SQLAlchemy', license: 'MIT License' },
            { name: 'Pydantic Settings', license: 'MIT License' },
            { name: 'HTTPX', license: 'BSD 3-Clause License' },
            { name: 'pywebview', license: 'BSD 3-Clause License' },
              { name: 'APScheduler', license: 'MIT License' },
              { name: 'win11toast', license: 'MIT License' },
              { name: 'python-multipart', license: 'Apache License 2.0' },
              { name: 'Pillow', license: 'HPND License' },
              { name: 'PyInstaller', license: 'GPL-2.0-or-later · 부트로더 예외' }
          ]
        },
        {
          name: '글꼴',
          items: [
            { name: 'Paperlogy', license: 'SIL Open Font License 1.1' },
              { name: 'Neo둥근모', license: 'SIL Open Font License 1.1', creator: 'Eunbin Jeong (Dalgona)' },
                { name: '얇은둥근모 v0.1', license: '제작자 고지 및 배포 조건', creator: 'sawalk' },
                { name: '굵은둥근모 v0.2', license: '제작자 고지 및 배포 조건', creator: 'sawalk' }
          ]
        }
      ],
      deleteMode: null,
      confirmDeleteType: null,
      dialogForm: { title: '', content: '', name: '', phone: '', time: '09:00' },
      settingsIcon,
      minimizeIcon,
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
    ...mapState(useThemeStore, ['accentColor', 'cssVariables', 'usePixelFont']),
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
      licenseScrollbarVisible() {
        return this.licenseScrollHeight > this.licenseClientHeight
      },
      licenseThumbStyle() {
        if (!this.licenseScrollbarVisible) return {}
        const thumbHeight = Math.max(18, (this.licenseClientHeight / this.licenseScrollHeight) * 100)
        const maxScrollTop = this.licenseScrollHeight - this.licenseClientHeight
        const top = (this.licenseScrollTop / maxScrollTop) * (100 - thumbHeight)

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
      const totalCells = 42

      return Array.from({ length: totalCells }, (_, index) => {
        const cellDate = new Date(this.year, this.month - 1, 1 - firstDayOffset + index)
        const year = cellDate.getFullYear()
        const month = cellDate.getMonth() + 1
        const date = cellDate.getDate()
        const isCurrentMonth = year === this.year && month === this.month

        return {
          key: index,
          year,
          month,
          date,
          isCurrentMonth,
          hasSchedule: this.schedules.some((schedule) => (
            schedule.year === year && schedule.month === month && schedule.day === date
          ))
        }
      })
    }
  },
  methods: {
    ...mapActions(useReminderStore, ['selectDay', 'selectDate', 'moveMonth', 'goToToday', 'addSchedule', 'toggleScheduleAlert', 'deleteSchedule', 'loadSchedules']),
    ...mapActions(useThemeStore, ['setAccentColor', 'setUsePixelFont', 'loadSettings']),
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
    minimizeWindow() {
      window.pywebview?.api?.minimize_window()
    },
    closeWindow() {
      window.pywebview?.api?.close_window()
    },
    startWindowResize(direction, event) {
      const resizeWindow = window.pywebview?.api?.resize_window
      if (typeof resizeWindow !== 'function') return

      this.windowResize = {
        direction,
        startX: event.screenX,
        startY: event.screenY,
        startWidth: window.innerWidth,
        startHeight: window.innerHeight,
        startWindowX: window.screenX,
        startWindowY: window.screenY
      }
      window.addEventListener('pointermove', this.resizeWindow)
      window.addEventListener('pointerup', this.stopWindowResize, { once: true })
      window.addEventListener('pointercancel', this.stopWindowResize, { once: true })
    },
    resizeWindow(event) {
      if (!this.windowResize) return

      const { direction, startX, startY, startWidth, startHeight, startWindowX, startWindowY } = this.windowResize
      const horizontalDelta = event.screenX - startX
      const verticalDelta = event.screenY - startY
      const width = Math.max(480, startWidth + (direction.includes('left') ? -horizontalDelta : direction.includes('right') ? horizontalDelta : 0))
      const height = Math.max(360, startHeight + (direction.includes('top') ? -verticalDelta : direction.includes('bottom') ? verticalDelta : 0))
      const actualWidth = Math.max(620, width)
      const actualHeight = Math.max(400, height)
      const x = direction.includes('left') ? startWindowX + startWidth - actualWidth : startWindowX
      const y = direction.includes('top') ? startWindowY + startHeight - actualHeight : startWindowY
      this.pendingWindowResize = { width: actualWidth, height: actualHeight, x, y }
      if (this.resizeRequestFrame !== null) return

      this.resizeRequestFrame = window.requestAnimationFrame(() => {
        this.resizeRequestFrame = null
        const resizeWindow = window.pywebview?.api?.resize_window
        const pending = this.pendingWindowResize
        if (typeof resizeWindow !== 'function' || !pending) return

        Promise.resolve(resizeWindow.call(
          window.pywebview.api,
          Math.round(pending.width),
          Math.round(pending.height),
          Math.round(pending.x),
          Math.round(pending.y)
        )).catch(() => {})
      })
    },
    stopWindowResize() {
      this.windowResize = null
      window.removeEventListener('pointermove', this.resizeWindow)
    },
    openSettings() {
      this.settingsAccentColor = this.accentColor
      this.isSettingsOpen = true
    },
    closeSettings() {
      this.isSettingsOpen = false
    },
      openLicenses() {
        this.isSettingsOpen = false
        this.isLicenseOpen = true
        this.$nextTick(this.updateLicenseScroll)
    },
    closeLicenses() {
      this.isLicenseOpen = false
    },
    async exportBackup() {
      try {
        const response = await apiClient.post('/backups/export')
        window.alert(`백업 파일을 다운로드 폴더에 저장했습니다.\n${response.data.path}`)
      } catch (error) {
        window.alert(error.response?.data?.detail || '백업 파일을 저장하지 못했습니다.')
      }
    },
    openBackupFilePicker() {
      this.$refs.backupFileInput.click()
    },
    selectBackupFile(event) {
      const [file] = event.target.files
      if (file) this.backupImportFile = file
      event.target.value = ''
    },
    cancelBackupImport() {
      this.backupImportFile = null
    },
    async confirmBackupImport() {
      const formData = new FormData()
      formData.append('file', this.backupImportFile)
      try {
        await apiClient.post('/backups/import', formData)
        await this.initializeData()
        this.backupImportFile = null
      } catch (error) {
        window.alert(error.response?.data?.detail || '백업 파일을 불러오지 못했습니다.')
      }
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
    async selectCalendarDay(day) {
      if (day.isCurrentMonth) {
        this.selectDay(day.date)
        return
      }

      await this.selectDate(day.year, day.month, day.date)
    },
    sanitizePhone() {
      this.dialogForm.phone = this.dialogForm.phone.replace(/[^0-9+-]/g, '')
    },
      async initializeData() {
        this.todayKey = new Date().toDateString()
        await Promise.all([this.loadMemos(), this.loadContacts(), this.loadSettings()])
        await this.goToToday()
      },
      async resetToTodayOnDateChange() {
        const todayKey = new Date().toDateString()
        if (todayKey === this.todayKey) return

        this.todayKey = todayKey
        await this.goToToday()
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
      updateLicenseScroll() {
        const list = this.$refs.licenseList
        if (!list) return
        this.licenseScrollTop = list.scrollTop
        this.licenseScrollHeight = list.scrollHeight
        this.licenseClientHeight = list.clientHeight
      },
      scrollLicenses(offset) {
        this.$refs.licenseList?.scrollBy({ top: offset, behavior: 'smooth' })
      },
      jumpLicenseScroll(event) {
        const track = this.$refs.licenseTrack
        const list = this.$refs.licenseList
        if (!track || !list) return
        const ratio = (event.clientY - track.getBoundingClientRect().top) / track.clientHeight
        list.scrollTop = ratio * (list.scrollHeight - list.clientHeight)
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
      this.dateChangeTimer = window.setInterval(this.resetToTodayOnDateChange, 60000)
      this.$nextTick(this.updateScheduleScroll)
  },
    updated() {
      this.$nextTick(this.updateScheduleScroll)
      this.$nextTick(this.updateLicenseScroll)
    this.$nextTick(this.updateMemoTextareaScroll)
    this.$nextTick(() => {
      this.updateSidebarListScroll('memo')
      this.updateSidebarListScroll('contact')
    })
  },
    beforeUnmount() {
      this.resizeObserver.disconnect()
      window.clearInterval(this.dateChangeTimer)
      this.stopWindowResize()
      if (this.resizeRequestFrame !== null) window.cancelAnimationFrame(this.resizeRequestFrame)
  }
}
</script>

<style src="./assets/styles/App.css"></style>

