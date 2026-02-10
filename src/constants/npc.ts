/**
 * NPC (Non-Player Character) identifiers in Travian.
 * These should be filtered out from player/alliance lists and charts.
 */
export const NPC_ALLIANCE = 'Natars'

/**
 * Check if an alliance tag is the NPC alliance (case-insensitive).
 */
export function isNpcAlliance(tag: string | null | undefined): boolean {
  if (!tag || typeof tag !== 'string') return false
  return tag.trim().toLowerCase() === 'natars'
}

/**
 * Filter out NPC alliance from a list of items with an alliance/tag field.
 */
export function filterNpcAlliances<T extends { alliance?: string; tag?: string }>(items: T[]): T[] {
  return items.filter((item) => {
    const tag = item.alliance ?? item.tag ?? ''
    return !isNpcAlliance(tag)
  })
}

/**
 * Filter out players belonging to NPC alliance.
 */
export function filterNpcPlayers<T extends { alliance?: string }>(items: T[]): T[] {
  return items.filter((item) => !isNpcAlliance(item.alliance))
}
