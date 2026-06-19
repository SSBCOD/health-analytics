import { createContext, useContext, useState } from 'react'
import kk from '../i18n/kk'
import ru from '../i18n/ru'

const translations = { kk, ru }
const LangContext = createContext()

export function LangProvider({ children }) {
  const [lang, setLang] = useState('ru')
  const t = (key) => translations[lang]?.[key] || key
  const apiLang = lang === 'kk' ? 'kz' : 'ru'

  return (
    <LangContext.Provider value={{ lang, setLang, t, apiLang }}>
      {children}
    </LangContext.Provider>
  )
}

export const useLang = () => useContext(LangContext)
