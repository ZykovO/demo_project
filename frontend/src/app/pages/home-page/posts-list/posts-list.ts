import {Component, Input} from '@angular/core';
import {Post} from '../../../data/interfaces/posts-interfaces';
import {PostCard} from './post-card/post-card';

@Component({
  selector: 'app-posts-list',
  imports: [
    PostCard
  ],
  templateUrl: './posts-list.html',
  styleUrl: './posts-list.css'
})
export class PostsList {
  @Input() posts: Post[] = [];
}
