#version 330 core

out vec4 FragColor;

// Dữ liệu từ Vertex Shader
in vec3 FragPos;
in vec3 Normal;

// --- Struct ---
struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

// Uniform
uniform vec3 viewPos;
uniform Material material;
uniform Light light;

void main()
{
    // 1. Ambient
    vec3 ambient = light.ambient * material.diffuse;
    
    // Normalize vector
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light.position - FragPos);
    
    // 2. Diffuse
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * diff * material.diffuse;
    
    // 3. Specular (PHONG SHADING CHUẨN)
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 reflectDir = reflect(-lightDir, norm);
    
    // Dot giữa viewDir và reflectDir
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * spec * material.specular;
    
    // Tổng
    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
}