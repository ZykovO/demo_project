import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {NotificationsComponent} from './common-ui/layout/notifications.component/notifications.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NotificationsComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected title = 'frontend';
}
