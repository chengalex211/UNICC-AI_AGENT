import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import NewEvaluation from './pages/NewEvaluation'
import ExpertAnalysis from './pages/ExpertAnalysis'
import CouncilReview from './pages/CouncilReview'
import FinalReport from './pages/FinalReport'

type Page = 'dashboard' | 'evaluate' | 'results' | 'council' | 'report'

function App() {
  const [page, setPage] = useState<Page>('dashboard')

  const handleSelectEval = (_id: string) => {
    setPage('results')
  }

  const handleEvalSubmit = () => {
    setPage('results')
  }

  return (
    <div className="flex min-h-screen bg-apple-gray-50">
      <Sidebar current={page} onChange={setPage} />
      <main className="flex-1 overflow-auto">
        {page === 'dashboard' && <Dashboard onSelect={handleSelectEval} />}
        {page === 'evaluate' && <NewEvaluation onSubmit={handleEvalSubmit} />}
        {page === 'results' && <ExpertAnalysis />}
        {page === 'council' && <CouncilReview />}
        {page === 'report' && <FinalReport />}
      </main>
    </div>
  )
}

export default App
