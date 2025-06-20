export interface UserResponse {
  id: number;
  email: string;
  username: string;
}

export interface TokenResponse {
  refresh:string
  access:string
  user:UserResponse
}

export interface RefreshTokenResponse {
  access:string
}
