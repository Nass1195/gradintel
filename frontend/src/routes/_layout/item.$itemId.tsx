import { createFileRoute } from '@tanstack/react-router'
import  UploadBox  from '@/components/ui/UploadBox'
import SummaryResult from "@/components/ui/SummaryResult"
import Quizes from '@/components/ui/quizes'
import { QuizQuestion } from "@/client/types.gen"


import { useState } from 'react'

export const Route = createFileRoute('/_layout/item/$itemId')({
  component: RouteComponent,
})

function RouteComponent() {
  const [summary, setSummary] = useState<string>(" ")
  const [quizQuestions, setQuizQuestions] = useState<Array<QuizQuestion>>([])



  return (
  <>
    <div style={{ display: "flex", flexDirection: "row", gap: "20px", paddingBottom: "20px", marginBottom: "20px", paddingTop: "20px", height: "100%" }}>
      <UploadBox onUploadStart={() => setSummary(" ")} onUploadSuccess={(text) => setSummary(text)} onUploadQuizSuccess={(quizes) => setQuizQuestions(quizes)} />
      <div style={{ width: "80%", height: "100%"}}>
        <SummaryResult content={summary} />
        <Quizes quizQuestions={quizQuestions} />
      </div>

     
    </div>
    
  </>
  )
}
