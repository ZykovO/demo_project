import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, ValidatorFn, AbstractControl } from '@angular/forms';
import { NgIf } from '@angular/common';
import { AuthService } from '../../auth/auth-service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-login-page',
  imports: [
    ReactiveFormsModule,
    NgIf
  ],
  templateUrl: './login-page.html',
  styleUrl: './login-page.css'
})
export class LoginPage {
  authService = inject(AuthService);
  router = inject(Router);
  isLoginMode = true;
  authForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.authForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      confirmPassword: ['']
    });

    // Инициализируем валидаторы в зависимости от начального режима
    this.updateValidators();
  }

  private updateValidators(): void {
    if (this.isLoginMode) {
      // В режиме входа - только базовые валидаторы
      this.authForm.get('email')?.setValidators([Validators.required, Validators.email]);
      this.authForm.get('password')?.setValidators([Validators.required]);
      this.authForm.get('confirmPassword')?.clearValidators();
    } else {
      // В режиме регистрации - добавляем проверку паролей
      this.authForm.get('email')?.setValidators([Validators.required, Validators.email]);
      this.authForm.get('password')?.setValidators([Validators.required]);
      this.authForm.get('confirmPassword')?.setValidators([Validators.required]);
      this.authForm.setValidators(this.passwordMatchValidator());
    }

    this.authForm.get('email')?.updateValueAndValidity();
    this.authForm.get('password')?.updateValueAndValidity();
    this.authForm.get('confirmPassword')?.updateValueAndValidity();
  }

  private passwordMatchValidator(): ValidatorFn {
    return (control: AbstractControl): { [key: string]: boolean } | null => {
      const formGroup = control as FormGroup;
      const password = formGroup.get('password')?.value;
      const confirmPassword = formGroup.get('confirmPassword')?.value;

      // Проверяем только если оба поля заполнены
      if (password && confirmPassword && password !== confirmPassword) {
        return { passwordMismatch: true };
      }
      return null;
    };
  }

  toggleMode(): void {
    this.isLoginMode = !this.isLoginMode;
    this.authForm.reset();
    this.updateValidators();
  }

  onSubmit(): void {
    this.authForm.markAllAsTouched();

    if (this.authForm.invalid) {
      console.log('Invalid form');
      return;
    }

    const { email, password } = this.authForm.value;

    if (this.isLoginMode) {
      this.authService.login(this.authForm.value).subscribe(result => {
        this.router.navigate(['/']);
      });
    } else {
      this.authService.register(this.authForm.value);
    }
  }
}
