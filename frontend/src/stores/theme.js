import { defineStore } from 'pinia'
import apiClient from '../api/client'


function clamp(value, minimum, maximum) {
  return Math.min(Math.max(value, minimum), maximum)
}

function hexToRgb(hex) {
  const normalized = hex.replace('#', '')
  const value = Number.parseInt(normalized, 16)

  return {
    red: (value >> 16) & 255,
    green: (value >> 8) & 255,
    blue: value & 255
  }
}

function rgbToHex(red, green, blue) {
  return `#${[red, green, blue]
    .map((value) => Math.round(clamp(value, 0, 255)).toString(16).padStart(2, '0'))
    .join('')}`
}

function rgbToHsv(red, green, blue) {
  const normalizedRed = red / 255
  const normalizedGreen = green / 255
  const normalizedBlue = blue / 255
  const maximum = Math.max(normalizedRed, normalizedGreen, normalizedBlue)
  const minimum = Math.min(normalizedRed, normalizedGreen, normalizedBlue)
  const difference = maximum - minimum
  let hue = 0

  if (difference) {
    if (maximum === normalizedRed) {
      hue = 60 * (((normalizedGreen - normalizedBlue) / difference) % 6)
    } else if (maximum === normalizedGreen) {
      hue = 60 * ((normalizedBlue - normalizedRed) / difference + 2)
    } else {
      hue = 60 * ((normalizedRed - normalizedGreen) / difference + 4)
    }
  }

  return {
    hue: (hue + 360) % 360,
    saturation: maximum ? difference / maximum : 0,
    value: maximum
  }
}

function hsvToRgb(hue, saturation, value) {
  const chroma = value * saturation
  const segment = hue / 60
  const secondary = chroma * (1 - Math.abs((segment % 2) - 1))
  const match = value - chroma
  let red = 0
  let green = 0
  let blue = 0

  if (segment < 1) {
    red = chroma
    green = secondary
  } else if (segment < 2) {
    red = secondary
    green = chroma
  } else if (segment < 3) {
    green = chroma
    blue = secondary
  } else if (segment < 4) {
    green = secondary
    blue = chroma
  } else if (segment < 5) {
    red = secondary
    blue = chroma
  } else {
    red = chroma
    blue = secondary
  }

  return {
    red: (red + match) * 255,
    green: (green + match) * 255,
    blue: (blue + match) * 255
  }
}

function isAchromatic(hsv) {
  return hsv.saturation < 0.01
}

function deriveColor(baseColor, saturationOffset, valueOffset) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)
  const rgb = hsvToRgb(
    hsv.hue,
    isAchromatic(hsv) ? 0 : clamp(hsv.saturation + saturationOffset, 0, 1),
    clamp(hsv.value + valueOffset, 0, 1)
  )

  return rgbToHex(rgb.red, rgb.green, rgb.blue)
}

function deriveHueColor(baseColor, saturation, value) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)
  const rgb = hsvToRgb(hsv.hue, isAchromatic(hsv) ? 0 : saturation, value)

  return rgbToHex(rgb.red, rgb.green, rgb.blue)
}

function deriveTitleTextColor(baseColor) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)
  const titleValue = clamp(hsv.value - 0.012, 0, 1)

  if (titleValue < 0.72) {
    return '#ffffff'
  }

  if (isAchromatic(hsv)) {
    return '#333333'
  }

  const rgb = hsvToRgb(hsv.hue, 0.78, 0.32)
  return rgbToHex(rgb.red, rgb.green, rgb.blue)
}

function deriveTextColor(baseColor) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)

  if (hsv.value < 0.72) {
    return '#ffffff'
  }

  return deriveColor(baseColor, -0.15, -0.7)
}

function deriveMutedTextColor(baseColor) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)

  if (hsv.value < 0.72) {
    return '#e8e8e8'
  }

  return deriveColor(baseColor, 0.32, -0.25)
}

function deriveButtonColor(baseColor) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)

  if (hsv.value < 0.72) {
    return deriveColor(baseColor, -0.12, 0.42)
  }

  return baseColor
}

function deriveScrollTrackColor(baseColor) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)

  if (hsv.value < 0.72) {
    return deriveColor(baseColor, -0.24, 0.08)
  }

  return deriveColor(baseColor, -0.42, 0.02)
}

function deriveAlertActiveColor(baseColor) {
  const { red, green, blue } = hexToRgb(baseColor)
  const hsv = rgbToHsv(red, green, blue)

  if (isAchromatic(hsv)) {
    return deriveColor(baseColor, 0, -0.38)
  }

  if (hsv.value < 0.72) {
    return deriveColor(baseColor, 0.28, 0.28)
  }

  return deriveColor(baseColor, 0.52, -0.18)
}


export const useThemeStore = defineStore('theme', {
  state: () => ({
    accentColor: '#ffdbd9',
    usePixelFont: typeof window === 'undefined' || window.localStorage.getItem('reminder.usePixelFont') !== 'false'
  }),
  getters: {
    cssVariables: (state) => ({
      '--theme-accent': state.accentColor,
      '--theme-button': deriveButtonColor(state.accentColor),
      '--theme-scroll-track': deriveScrollTrackColor(state.accentColor),
      '--theme-page': deriveHueColor(state.accentColor, 0.035, 0.995),
      '--theme-adjacent-day': deriveHueColor(state.accentColor, 0.01, 1),
      '--theme-panel': deriveColor(state.accentColor, -0.42, 0.02),
      '--theme-light': deriveColor(state.accentColor, -0.5, 0.12),
      '--theme-highlight': deriveColor(state.accentColor, -0.28, 0.07),
      '--theme-pressed': deriveColor(state.accentColor, 0.06, -0.14),
      '--theme-shadow': deriveColor(state.accentColor, 0.12, -0.28),
      '--theme-dark': deriveColor(state.accentColor, 0.16, -0.48),
      '--theme-title-dark': deriveColor(state.accentColor, 0.38, -0.1),
      '--theme-title': deriveColor(state.accentColor, 0.2, -0.012),
      '--theme-title-muted': deriveColor(state.accentColor, 0.03, -0.25),
      '--theme-date-text': deriveColor(state.accentColor, 0.34, -0.012),
      '--theme-date-muted': deriveMutedTextColor(state.accentColor),
      '--theme-date-active': deriveAlertActiveColor(state.accentColor),
      '--theme-title-text': deriveTitleTextColor(state.accentColor),
      '--theme-text': deriveTextColor(state.accentColor),
      '--theme-surface-text': deriveColor(state.accentColor, -0.15, -0.7)
    })
  },
  actions: {
    async loadSettings() {
      const { data } = await apiClient.get('/settings')
      this.accentColor = data.accent_color
    },
    async setAccentColor(color) {
      this.accentColor = color
      await apiClient.patch('/settings', { accent_color: color })
    },
    setUsePixelFont(usePixelFont) {
      this.usePixelFont = usePixelFont
      window.localStorage.setItem('reminder.usePixelFont', String(usePixelFont))
    }
  }
})
