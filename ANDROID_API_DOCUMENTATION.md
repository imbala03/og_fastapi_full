# Android API Integration Guide - Login Endpoint

## Login Endpoint

### Base URL
```
http://127.0.0.1:8000
```

**Note:** For Android emulator, use `http://10.0.2.2:8000` instead of `127.0.0.1`
**Note:** For physical device on same network, use your computer's IP address (e.g., `http://192.168.1.100:8000`)

### Endpoint
```
POST /auth/login
```

### Full URL
```
http://127.0.0.1:8000/auth/login
```

### Request Headers
```
Content-Type: application/json
Accept: application/json
```

### Request Body
```json
{
  "identifier": "mail4bala03@gmail.com",
  "password": "Bala03@rx3"
}
```

**Fields:**
- `identifier` (string, required): Email address or phone number
- `password` (string, required): User password (plain text)

### Success Response (200 OK)
```json
{
  "id": 3,
  "name": "Bala",
  "email": "mail4bala03@gmail.com",
  "phone": "9739674474",
  "role": "poweradmin",
  "status": "1",
  "last_login": "2025-11-28T23:48:10.434284+05:30",
  "created_at": "2025-11-28T23:20:05.362478+05:30",
  "updated_at": "2025-11-28T23:48:10.056098+05:30"
}
```

### Error Responses

#### 401 Unauthorized - Invalid Credentials
```json
{
  "detail": "Invalid credentials"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error message]"
}
```

---

## Android Implementation Examples

### Using Retrofit (Recommended)

#### 1. Add Dependencies to `build.gradle` (Module: app)
```gradle
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
}
```

#### 2. Add Internet Permission to `AndroidManifest.xml`
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

#### 3. Create Data Models

**LoginRequest.kt**
```kotlin
data class LoginRequest(
    val identifier: String,
    val password: String
)
```

**UserResponse.kt**
```kotlin
import com.google.gson.annotations.SerializedName
import java.util.Date

data class UserResponse(
    val id: Int,
    val name: String,
    val email: String?,
    val phone: String?,
    val role: String,
    val status: String,
    @SerializedName("last_login")
    val lastLogin: String?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
)
```

**ErrorResponse.kt**
```kotlin
data class ErrorResponse(
    val detail: String
)
```

#### 4. Create API Interface

**ApiService.kt**
```kotlin
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface ApiService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<UserResponse>
}
```

#### 5. Create Retrofit Instance

**RetrofitClient.kt**
```kotlin
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    // Change this URL based on your setup:
    // - Emulator: http://10.0.2.2:8000
    // - Physical device: http://YOUR_COMPUTER_IP:8000
    // - Production: https://your-domain.com
    private const val BASE_URL = "http://10.0.2.2:8000/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

#### 6. Use in Activity/Fragment

**LoginActivity.kt**
```kotlin
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        
        // Example login call
        loginUser("mail4bala03@gmail.com", "Bala03@rx3")
    }
    
    private fun loginUser(email: String, password: String) {
        lifecycleScope.launch {
            try {
                val request = LoginRequest(
                    identifier = email,
                    password = password
                )
                
                val response = RetrofitClient.apiService.login(request)
                
                if (response.isSuccessful && response.body() != null) {
                    val user = response.body()!!
                    // Handle successful login
                    Toast.makeText(
                        this@LoginActivity,
                        "Login successful! Welcome ${user.name}",
                        Toast.LENGTH_SHORT
                    ).show()
                    
                    // Save user data, navigate to next screen, etc.
                    // Example: saveUserData(user)
                    // Example: navigateToHome()
                    
                } else {
                    // Handle error
                    val errorBody = response.errorBody()?.string()
                    Toast.makeText(
                        this@LoginActivity,
                        "Login failed: ${errorBody ?: "Unknown error"}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            } catch (e: Exception) {
                // Handle network/connection errors
                Toast.makeText(
                    this@LoginActivity,
                    "Network error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
                e.printStackTrace()
            }
        }
    }
}
```

---

### Using OkHttp (Alternative)

```kotlin
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

class LoginApiClient {
    private val client = OkHttpClient()
    private val baseUrl = "http://10.0.2.2:8000"
    
    fun login(email: String, password: String, callback: (UserResponse?, String?) -> Unit) {
        val json = JSONObject().apply {
            put("identifier", email)
            put("password", password)
        }
        
        val requestBody = json.toString()
            .toRequestBody("application/json".toMediaType())
        
        val request = Request.Builder()
            .url("$baseUrl/auth/login")
            .post(requestBody)
            .addHeader("Content-Type", "application/json")
            .addHeader("Accept", "application/json")
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback(null, "Network error: ${e.message}")
            }
            
            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                if (response.isSuccessful && responseBody != null) {
                    // Parse JSON response
                    // Use Gson or JSONObject to parse
                    callback(parsedUser, null)
                } else {
                    callback(null, "Error: ${response.code} - $responseBody")
                }
            }
        })
    }
}
```

---

## Important Notes for Android

### 1. Network Security Configuration
For Android 9+ (API 28+), you need to allow cleartext traffic:

**res/xml/network_security_config.xml**
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">127.0.0.1</domain>
    </domain-config>
</network-security-config>
```

**AndroidManifest.xml**
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### 2. URL Configuration

- **Android Emulator**: Use `http://10.0.2.2:8000` (maps to host's localhost)
- **Physical Device (Same Network)**: Use `http://YOUR_COMPUTER_IP:8000`
  - Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- **Production**: Use your production server URL with HTTPS

### 3. Testing URLs

```kotlin
// For emulator
private const val BASE_URL = "http://10.0.2.2:8000/"

// For physical device (replace with your computer's IP)
private const val BASE_URL = "http://192.168.1.100:8000/"

// For production
private const val BASE_URL = "https://your-api-domain.com/"
```

---

## Quick Test with cURL (for reference)

```bash
curl -X POST \
  'http://127.0.0.1:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "identifier": "mail4bala03@gmail.com",
    "password": "Bala03@rx3"
  }'
```

---

## Response Fields Explanation

- `id`: User ID
- `name`: User's full name
- `email`: User's email address
- `phone`: User's phone number
- `role`: User role (super_admin, admin, agent, customer, poweradmin)
- `status`: User status
- `last_login`: Last login timestamp (ISO 8601 format)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp




