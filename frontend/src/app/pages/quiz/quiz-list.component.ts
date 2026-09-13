import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface QuestionDraft {
  text: string;
  options: string[];
  correct_index: number;
}

@Component({
  selector: 'app-quiz-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './quiz-list.component.html'
})
export class QuizListComponent implements OnInit, OnDestroy {
  apiUrl = 'https://hr-management-api-6rpx.onrender.com/operations/quizzes';
  userRole = localStorage.getItem('role') || 'PERSONEL';

  quizzes: any[] = [];
  activeQuiz: any = null;
  selectedAnswers: number[] = [];
  timerSeconds = 0;
  timerInterval: any = null;

  showModal = false;
  newTitle = '';
  newDuration = 15;
  newQuestions: QuestionDraft[] = [
    { text: '', options: ['', ''], correct_index: 0 }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadQuizzes();
  }

  ngOnDestroy(): void {
    if (this.timerInterval) clearInterval(this.timerInterval);
  }

  loadQuizzes(): void {
    this.http.get<any[]>(this.apiUrl).subscribe({
      next: (res) => (this.quizzes = res),
      error: (err) => console.error(err)
    });
  }

  startQuiz(quiz: any): void {
    this.activeQuiz = quiz;
    this.selectedAnswers = new Array(quiz.questions.length).fill(-1);
    this.timerSeconds = quiz.duration_minutes * 60;

    if (this.timerInterval) clearInterval(this.timerInterval);
    this.timerInterval = setInterval(() => {
      if (this.timerSeconds > 0) {
        this.timerSeconds--;
      } else {
        this.finishQuiz();
      }
    }, 1000);
  }

  finishQuiz(): void {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.http.post(`${this.apiUrl}/${this.activeQuiz.id}/submit`, {
      selected_answers: this.selectedAnswers
    }).subscribe({
      next: () => {
        alert('Quiz tamamlandı ve sonucunuz kaydedildi!');
        this.activeQuiz = null;
        this.loadQuizzes();
      },
      error: (err) => alert(err.error?.detail || 'Hata oluştu')
    });
  }

  get formattedTime(): string {
    const mins = Math.floor(this.timerSeconds / 60);
    const secs = this.timerSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  addQuestion(): void {
    this.newQuestions.push({ text: '', options: ['', ''], correct_index: 0 });
  }

  removeQuestion(idx: number): void {
    if (this.newQuestions.length > 1) this.newQuestions.splice(idx, 1);
  }

  addOption(qIdx: number): void {
    this.newQuestions[qIdx].options.push('');
  }

  removeOption(qIdx: number, optIdx: number): void {
    if (this.newQuestions[qIdx].options.length > 2) {
      this.newQuestions[qIdx].options.splice(optIdx, 1);
      if (this.newQuestions[qIdx].correct_index >= this.newQuestions[qIdx].options.length) {
        this.newQuestions[qIdx].correct_index = 0;
      }
    }
  }

  saveQuiz(): void {
    const payload = {
      title: this.newTitle,
      duration_minutes: this.newDuration,
      questions: this.newQuestions
    };
    this.http.post(this.apiUrl, payload).subscribe({
      next: () => {
        this.showModal = false;
        this.newTitle = '';
        this.newQuestions = [{ text: '', options: ['', ''], correct_index: 0 }];
        this.loadQuizzes();
      },
      error: (err) => alert('Quiz kaydedilemedi: ' + err.message)
    });
  }
}
