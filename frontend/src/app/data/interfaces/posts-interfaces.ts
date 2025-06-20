export interface Attachment{
  id: number;
  file_type: string;
  file_url: string;
  image_url: string;
  thumbnail_url: string;
  upload_at: Date;
}
export interface Comment {
  id: number;
  author: string;
  author_username: string;
  content: string;
  created_at: Date;
  updated_at: Date;
  parent: number;
  post:number;
  post_title:string;
  is_deleted: boolean;
  attachments: Attachment[];
  replies_count: number;
  replies: Comment[];
}

export interface Post {
  id: number;
  author: string;
  author_username: string;
  title: string;
  content: string;
  is_published: boolean;
  created_at: Date;
  updated_at: Date;
  attachments: Attachment[];
  comments_count: number;
  recent_comments: Comment[];
}
