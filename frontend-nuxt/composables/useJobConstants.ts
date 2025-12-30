// frontend-nuxt/composables/useJobConstants.ts

// Use Sets for O(1) lookup performance
const adminSysnamSet = new Set<string>([
    '綜合行政', '人事行政', '經建行政', '會計審計', '文教行政', '社勞行政',
    '地政', '衛生行政', '法制', '交通行政', '社會工作', '司法行政',
    '廉政', '統計', '環保行政', '海巡行政', '新聞傳播', '財稅金融'
])

const techSysnamSet = new Set<string>([
    '土木工程', '電機工程', '資訊處理', '農業技術', '測量製圖',
    '建築工程', '交通技術', '獸醫', '衛生技術', '機械工程', '都市計畫',
    '動物技術', '景觀設計', '環資技術', '工業工程', '自然保育', '圖書史料檔案',
    '地質礦治', '職業安全衛生', '醫學工程', '林業技術', '消防技術', '技藝',
    '消防與災害防救', '化學工程'
])

export const useJobConstants = () => {
    // Export arrays for backwards compatibility (e.g., SysnamModal)
    const adminSysnams = Array.from(adminSysnamSet)
    const techSysnams = Array.from(techSysnamSet)

    /**
     * Determine the type of a job category (sysnam)
     * @returns 'admin' for administrative, 'tech' for technical, 'unknown' for others
     */
    const getSysnamType = (sysnam: string | undefined): 'admin' | 'tech' | 'unknown' => {
        if (!sysnam) return 'unknown'
        if (adminSysnamSet.has(sysnam)) return 'admin'
        if (techSysnamSet.has(sysnam)) return 'tech'
        return 'unknown'
    }

    return {
        adminSysnams,
        techSysnams,
        getSysnamType
    }
}
