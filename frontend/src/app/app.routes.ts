import { Routes } from '@angular/router';
import {HomePage} from './pages/home-page/home-page';
import {ProfilePage} from './pages/profile-page/profile-page';
import {LoginPage} from './pages/login-page/login-page';
import {Layout} from './common-ui/layout/layout';
import {canActivateAuth} from './auth/access.guard';
import {ProfilePostsPage} from './pages/profile-posts-page/profile-posts-page';

export const routes: Routes = [
  {path: '', component: Layout, children: [
      { path: 'profile', component: ProfilePage,canActivate:[canActivateAuth] },
      { path: '', component: HomePage},
      { path: 'posts', component: ProfilePostsPage}
    ]},
  { path: 'login', component: LoginPage },

];
