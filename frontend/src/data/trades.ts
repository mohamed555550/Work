export interface TradeCategory {
  id: string
  name: string
}

export interface Trade {
  id: string
  name: string
  icon: string
  image: string
  categories: TradeCategory[]
}

export const trades: Trade[] = [
  { id: 'all', name: 'كل المهن', icon: '◎', image: '/backgrounds/trades/01-carpenter.jpg', categories: [{ id: 'all', name: 'يظهر في كل المهن' }] },
  { id: 'carpenter', name: 'نجار', icon: '▰', image: '/backgrounds/trades/01-carpenter.jpg', categories: [
    { id: 'doors-windows', name: 'أبواب وشبابيك' }, { id: 'furniture', name: 'أثاث وموبيليا' }, { id: 'wood-kitchens', name: 'مطابخ خشب' }, { id: 'wood-repairs', name: 'تصليح خشب' },
  ] },
  { id: 'electrician', name: 'كهربائي', icon: 'ϟ', image: '/backgrounds/trades/02-electrician.jpg', categories: [
    { id: 'home-wiring', name: 'تأسيس كهرباء' }, { id: 'faults', name: 'أعطال منزلية' }, { id: 'lighting', name: 'إضاءة وسبوتات' }, { id: 'panels', name: 'لوحات ومفاتيح' },
  ] },
  { id: 'plumber', name: 'سباك', icon: '⌁', image: '/backgrounds/trades/03-plumber.jpg', categories: [
    { id: 'pipes-drain', name: 'مواسير وصرف' }, { id: 'bathrooms', name: 'حمامات' }, { id: 'heaters', name: 'سخانات' }, { id: 'leaks', name: 'كشف تسريب' },
  ] },
  { id: 'painter', name: 'نقاش', icon: '●', image: '/backgrounds/trades/04-painter.jpg', categories: [
    { id: 'interior-paint', name: 'دهانات داخلية' }, { id: 'facade-paint', name: 'واجهات' }, { id: 'decor-paint', name: 'ديكور وملمس' }, { id: 'wallpaper', name: 'ورق حائط' },
  ] },
  { id: 'blacksmith', name: 'حداد', icon: '⌘', image: '/backgrounds/trades/05-blacksmith.jpg', categories: [
    { id: 'iron-doors', name: 'أبواب حديد' }, { id: 'window-grills', name: 'شبابيك وحمايات' }, { id: 'stairs-rails', name: 'سلالم ودرابزين' }, { id: 'metal-repair', name: 'لحام وتصليح' },
  ] },
  { id: 'tiler', name: 'سيراميك وبلاط', icon: '▦', image: '/backgrounds/trades/06-tiler.jpg', categories: [
    { id: 'ceramic', name: 'تركيب سيراميك' }, { id: 'porcelain', name: 'بورسلين' }, { id: 'bathroom-tiles', name: 'حمامات ومطابخ' }, { id: 'tile-repair', name: 'ترميم وفواصل' },
  ] },
  { id: 'mason', name: 'بناء ومحارة', icon: '▥', image: '/backgrounds/trades/07-mason.jpg', categories: [
    { id: 'brickwork', name: 'مباني وطوب' }, { id: 'plaster', name: 'محارة' }, { id: 'cement-work', name: 'خرسانة خفيفة' }, { id: 'renovation', name: 'ترميم' },
  ] },
  { id: 'ac', name: 'تكييف وتبريد', icon: '❄', image: '/backgrounds/trades/08-ac-technician.jpg', categories: [
    { id: 'ac-install', name: 'تركيب تكييف' }, { id: 'ac-maintenance', name: 'صيانة تكييف' }, { id: 'gas-charge', name: 'شحن فريون' }, { id: 'ventilation', name: 'تهوية ودكت' },
  ] },
  { id: 'appliances', name: 'صيانة أجهزة', icon: '▣', image: '/backgrounds/trades/09-appliance-repair.jpg', categories: [
    { id: 'washing-machines', name: 'غسالات' }, { id: 'fridges', name: 'ثلاجات' }, { id: 'cookers', name: 'بوتاجازات' }, { id: 'screens', name: 'شاشات' },
  ] },
  { id: 'upholstery', name: 'تنجيد وستائر', icon: '▭', image: '/backgrounds/trades/10-upholsterer.jpg', categories: [
    { id: 'sofas', name: 'كنب وأنتريهات' }, { id: 'curtains', name: 'ستائر' }, { id: 'mattresses', name: 'مراتب' }, { id: 'fabric-repair', name: 'تصليح قماش' },
  ] },
  { id: 'aluminum', name: 'ألوميتال', icon: '▤', image: '/backgrounds/trades/11-aluminum.jpg', categories: [
    { id: 'aluminum-windows', name: 'شبابيك ألوميتال' }, { id: 'aluminum-doors', name: 'أبواب ألوميتال' }, { id: 'aluminum-kitchens', name: 'مطابخ ألوميتال' }, { id: 'aluminum-maintenance', name: 'صيانة قطاعات' },
  ] },
  { id: 'glass', name: 'زجاج ومرايات', icon: '◇', image: '/backgrounds/trades/12-glass.jpg', categories: [
    { id: 'mirrors', name: 'مرايات' }, { id: 'glass-facades', name: 'واجهات زجاج' }, { id: 'shower-glass', name: 'شاور زجاج' }, { id: 'glass-repair', name: 'تغيير زجاج' },
  ] },
  { id: 'gypsum', name: 'جبس بورد', icon: '▧', image: '/backgrounds/trades/13-gypsum.jpg', categories: [
    { id: 'ceilings', name: 'أسقف' }, { id: 'partitions', name: 'قواطيع' }, { id: 'light-box', name: 'بيت نور' }, { id: 'gypsum-decor', name: 'ديكورات' },
  ] },
  { id: 'locksmith', name: 'مفاتيح وكوالين', icon: '◉', image: '/backgrounds/trades/14-locksmith.jpg', categories: [
    { id: 'copy-keys', name: 'نسخ مفاتيح' }, { id: 'change-locks', name: 'تغيير كالون' }, { id: 'open-doors', name: 'فتح أبواب' }, { id: 'smart-locks', name: 'أقفال ذكية' },
  ] },
  { id: 'network', name: 'شبكات وكاميرات', icon: '◍', image: '/backgrounds/trades/15-network.jpg', categories: [
    { id: 'cctv', name: 'كاميرات مراقبة' }, { id: 'internet', name: 'شبكات إنترنت' }, { id: 'router', name: 'راوتر وتقوية إشارة' }, { id: 'smart-home', name: 'سمارت هوم' },
  ] },
  { id: 'cleaning', name: 'تنظيف', icon: '✦', image: '/backgrounds/trades/16-cleaning.jpg', categories: [
    { id: 'home-cleaning', name: 'تنظيف منازل' }, { id: 'carpets', name: 'سجاد وموكيت' }, { id: 'facade-cleaning', name: 'واجهات' }, { id: 'post-finishing', name: 'بعد التشطيب' },
  ] },
  { id: 'roofing', name: 'عزل أسطح', icon: '⌂', image: '/backgrounds/trades/17-roofing.jpg', categories: [
    { id: 'waterproofing', name: 'عزل مياه' }, { id: 'heat-insulation', name: 'عزل حراري' }, { id: 'foam', name: 'فوم' }, { id: 'bitumen', name: 'بيتومين' },
  ] },
  { id: 'mechanic', name: 'ميكانيكي سيارات', icon: '◌', image: '/backgrounds/trades/18-mechanic.jpg', categories: [
    { id: 'engine', name: 'موتور' }, { id: 'brakes', name: 'فرامل' }, { id: 'oil-service', name: 'زيوت وصيانة دورية' }, { id: 'diagnostics', name: 'كشف كمبيوتر' },
  ] },
  { id: 'mobile', name: 'صيانة موبايلات', icon: '▯', image: '/backgrounds/trades/19-mobile-repair.jpg', categories: [
    { id: 'screens', name: 'شاشات' }, { id: 'batteries', name: 'بطاريات' }, { id: 'software', name: 'سوفت وير' }, { id: 'charging', name: 'سوكت شحن' },
  ] },
  { id: 'tailor', name: 'ترزي', icon: '✂', image: '/backgrounds/trades/20-tailor.jpg', categories: [
    { id: 'men-tailoring', name: 'رجالي' }, { id: 'women-tailoring', name: 'حريمي' }, { id: 'alterations', name: 'تعديل مقاسات' }, { id: 'uniforms', name: 'يونيفورم' },
  ] },
  { id: 'factory-workers', name: 'عمال مصانع', icon: '▦', image: '/backgrounds/trades/15-network.jpg', categories: [
    { id: 'production-line', name: 'عمال خطوط إنتاج' }, { id: 'packing', name: 'تعبئة وتغليف' }, { id: 'quality-control', name: 'مراقبة جودة' }, { id: 'warehouse', name: 'مخازن وتحميل' }, { id: 'machine-operator', name: 'تشغيل ماكينات' }, { id: 'cnc-operator', name: 'تشغيل CNC' }, { id: 'mechanical-maintenance', name: 'صيانة ميكانيكية' }, { id: 'electrical-maintenance', name: 'صيانة كهرباء صناعية' }, { id: 'welding', name: 'لحام صناعي' }, { id: 'lathe', name: 'خراطة وفريزة' }, { id: 'plastic-factories', name: 'مصانع بلاستيك' }, { id: 'food-factories', name: 'مصانع أغذية' }, { id: 'textile-factories', name: 'مصانع نسيج' }, { id: 'garment-factories', name: 'مصانع ملابس' }, { id: 'pharma-factories', name: 'مصانع أدوية' }, { id: 'chemical-factories', name: 'مصانع كيماويات' }, { id: 'printing-factories', name: 'مطابع وتغليف ورقي' }, { id: 'furniture-factories', name: 'مصانع أثاث' }, { id: 'metal-factories', name: 'مصانع معادن' }, { id: 'safety', name: 'سلامة وصحة مهنية' }, { id: 'industrial-cleaning', name: 'نظافة صناعية' },
  ] },
]

export const selectableTrades = trades.filter((trade) => trade.id !== 'all')

export function findTrade(id?: string) {
  return trades.find((trade) => trade.id === id) || trades[1]
}

export function findTradeCategory(tradeId?: string, categoryId?: string) {
  const trade = findTrade(tradeId)
  return trade.categories.find((category) => category.id === categoryId) || trade.categories[0]
}
