/**
 * Haptic (tactile) feedback for buttons and interactive elements.
 * Uses Vibration API when available (mobile/supported browsers); no-op otherwise.
 */

const LIGHT = 10
const MEDIUM = 15
const HEAVY = 25

export function hapticLight(): void {
  if (typeof navigator !== 'undefined' && navigator.vibrate) {
    navigator.vibrate(LIGHT)
  }
}

export function hapticMedium(): void {
  if (typeof navigator !== 'undefined' && navigator.vibrate) {
    navigator.vibrate(MEDIUM)
  }
}

export function hapticHeavy(): void {
  if (typeof navigator !== 'undefined' && navigator.vibrate) {
    navigator.vibrate(HEAVY)
  }
}

/** Call on button/tap; use for primary actions (submit, confirm). */
export function hapticButton(): void {
  hapticMedium()
}

/** Call on nav/item selection (tabs, list items). */
export function hapticSelect(): void {
  hapticLight()
}
