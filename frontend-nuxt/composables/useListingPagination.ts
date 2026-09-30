import { computed, ref, watch } from 'vue'

const readNumber = (value: unknown, fallback: number, maximum: number) => {
  if (typeof value !== 'string' || !/^[1-9]\d*$/.test(value)) return fallback
  const number = Number(value)
  return Number.isSafeInteger(number) && number <= maximum ? number : fallback
}

export const useListingPagination = (defaultPerPage = 20) => {
  const route = useRoute()
  const router = useRouter()
  const currentPage = ref(readNumber(route.query.page, 1, 1000))
  const perPage = ref(readNumber(route.query.per_page, defaultPerPage, 100))

  watch(() => [route.path, route.query], () => {
    currentPage.value = readNumber(route.query.page, 1, 1000)
    perPage.value = readNumber(route.query.per_page, defaultPerPage, 100)
  })

  const paginationQuery = computed(() => {
    const query = new URLSearchParams()
    if (currentPage.value > 1) query.set('page', String(currentPage.value))
    if (perPage.value !== defaultPerPage) query.set('per_page', String(perPage.value))
    return query.toString()
  })

  const updatePagination = (page: number, pageSize = perPage.value) => {
    currentPage.value = readNumber(String(page), 1, 1000)
    perPage.value = readNumber(String(pageSize), defaultPerPage, 100)
    return router.push({
      query: {
        ...route.query,
        page: currentPage.value > 1 ? String(currentPage.value) : undefined,
        per_page: perPage.value !== defaultPerPage ? String(perPage.value) : undefined
      }
    })
  }

  return { currentPage, perPage, paginationQuery, updatePagination }
}
