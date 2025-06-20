import {Component, inject} from '@angular/core';
import {PostsService} from '../../data/services/posts-service';
import {Post} from '../../data/interfaces/posts-interfaces';
import {JsonPipe} from '@angular/common';
import {PostsList} from './posts-list/posts-list';


@Component({
  selector: 'app-home-page',
  imports: [
    JsonPipe,
    PostsList,
  ],
  templateUrl: './home-page.html',
  styleUrl: './home-page.css'
})
export class HomePage {
  postsService=inject(PostsService);
  posts:Post[]=[];

  ngOnInit() {
    this.postsService.getAllPosts().subscribe((posts: Post[]) => {
      this.posts = posts;
      console.log(this.posts);
    })
  }
}
