// frontend-nuxt/composables/useJobConstants.ts

export const useJobConstants = () => {
    const adminSysnams: string[] = [
        '綜合行政', '人事行政', '經建行政', '會計審計', '文教行政', '社勞行政',
        '地政', '衛生行政', '法制', '交通行政', '社會工作', '司法行政',
        '廉政', '統計', '環保行政', '海巡行政', '新聞傳播'
    ]

    const techSysnams: string[] = [
        '土木工程', '電機工程', '資訊處理', '財稅金融', '農業技術', '測量製圖',
        '建築工程', '交通技術', '獸醫', '衛生技術', '機械工程', '都市計畫',
        '動物技術', '景觀設計', '環資技術', '工業工程', '自然保育', '圖書史料檔案',
        '地質礦治', '職業安全衛生', '醫學工程', '林業技術', '消防技術', '技藝',
        '消防與災害防救', '化學工程'
    ]

    return {
        adminSysnams,
        techSysnams
    }
}
