# Experiencia de Usuario y Diseño Web

**Requisito Extra:** 0.25 puntos  
**Estado:** ✅ Implementado

## 🎨 Descripción

Interfaz web moderna y profesional con diseño responsive, efectos visuales y experiencia de usuario optimizada.

## 📱 Páginas Implementadas

### 1. Página de Login (`index.html`)
- Formulario de autenticación
- Diseño centrado y responsive
- Efectos hover y focus

### 2. Página de Éxito (`success.html`)
- Confirmación de acceso concedido
- Información de estado de conexión
- Mismo estilo visual consistente

## 🎯 Características de Diseño

### Esquema de Colores
```css
Gradiente Principal: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Color de Texto: #333 (títulos), #666 (subtítulos), #555 (labels)
Color de Fondo: white (cajas), transparent (body con gradiente)
Color de Acento: #667eea (focus, hover)
```

### Tipografía
```css
Font Family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
Tamaños:
  - H1: 24-28px
  - Párrafos: 14-16px
  - Labels: 14px
  - Footer: 12-13px
```

## 💎 Elementos Destacados

### 1. Gradiente de Fondo
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
min-height: 100vh;
```
- Degradado diagonal suave
- Colores púrpura/violeta modernos
- Cubre toda la pantalla

### 2. Iconos SVG
```html
<!-- Icono de usuario en login -->
<svg viewBox="0 0 24 24">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10..."/>
</svg>

<!-- Icono de check en success -->
<svg viewBox="0 0 24 24">
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19..."/>
</svg>
```
- SVG inline (no dependencias externas)
- Escalables sin pérdida de calidad
- Fácil personalización de colores

### 3. Efectos Hover en Botón
```css
button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

button:active {
    transform: translateY(0);
}
```
- Elevación al pasar mouse
- Sombra dinámica
- Feedback táctil al hacer click

### 4. Inputs con Transiciones
```css
input:focus {
    outline: none;
    border-color: #667eea;
    transition: border-color 0.3s;
}
```
- Borde cambia de color suavemente
- Sin outline por defecto (antiestético)
- Feedback visual claro

### 5. Cajas con Profundidad
```css
.container {
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    border-radius: 10px;
}
```
- Sombras para sensación de elevación
- Bordes redondeados modernos
- Contraste con el fondo

## 📐 Diseño Responsive

### Mobile First
```css
.container {
    max-width: 420px;
    width: 100%;
    padding: 40px;
}

@media (max-width: 480px) {
    .container {
        padding: 30px 20px;
    }
}
```

### Viewport Meta Tag
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

## 🎭 Aspectos de UX

### 1. Claridad
- Mensajes simples sin jerga técnica
- "Bienvenido" en lugar de "Sistema de Autenticación Multifactor"
- Instrucciones directas

### 2. Feedback Visual
- Colores cambian al interactuar
- Estados claros (hover, focus, active)
- Iconos refuerzan el mensaje

### 3. Accesibilidad
```html
<label for="username">Usuario</label>
<input type="text" id="username" name="username" autocomplete="username">
```
- Labels asociados a inputs
- Autocomplete habilitado
- Contraste de colores adecuado

### 4. Consistencia
- Mismo esquema de colores en todas las páginas
- Tipografía uniforme
- Espaciado coherente

### 5. Branding
```html
<div class="footer">
    <p>Portal Cautivo - Proyecto Redes 2025</p>
</div>
```
- Footer personalizado
- Identidad visual propia

## 📊 Comparación: Antes vs Después

### Antes (Diseño Básico)
```html
<style>
body{font-family:Arial;background:#f5f5f5;padding:2rem}
.box{background:white;padding:1.5rem}
input{width:100%;padding:.6rem}
</style>
```
- Fondo gris plano
- Sin iconos
- Sin efectos
- Sin gradientes

### Después (Diseño Moderno)
```html
<style>
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}
.container{box-shadow:0 10px 25px rgba(0,0,0,.2)}
button:hover{transform:translateY(-2px)}
</style>
```
- Gradiente degradado
- Iconos SVG
- Efectos hover
- Sombras dinámicas

## 🖼️ Estructura Visual

### Login Page
```
┌────────────────────────────────┐
│      [Icono Usuario SVG]       │
│                                │
│         Bienvenido             │
│  Inicia sesión para acceder    │
│                                │
│  Usuario:                      │
│  [____________________]        │
│                                │
│  Contraseña:                   │
│  [____________________]        │
│                                │
│      [  Conectarse  ]          │← Botón con gradiente
│                                │
│  Portal Cautivo - 2025         │
└────────────────────────────────┘
```

### Success Page
```
┌────────────────────────────────┐
│       [Icono Check ✓]          │
│                                │
│    ¡Conexión Exitosa!          │
│                                │
│ Tu dispositivo ya tiene acceso │
│   a Internet. Puedes navegar   │
│      libremente por la red.    │
│                                │
│ ┌────────────────────────────┐ │
│ │ Estado: Conectado          │ │
│ │ Acceso: Completo           │ │
│ │ Nota: Sesión permanecerá   │ │
│ └────────────────────────────┘ │
│                                │
│  Portal Cautivo - 2025         │
└────────────────────────────────┘
```

## ✅ Verificación del Requisito

- ✅ Diseño profesional y moderno
- ✅ Responsive (funciona en mobile y desktop)
- ✅ Efectos hover y transiciones
- ✅ Iconos SVG personalizados
- ✅ Gradientes y sombras
- ✅ Experiencia de usuario optimizada
- ✅ Consistencia visual
- ✅ Sin dependencias externas (no Bootstrap, no jQuery)

## 🎨 Paleta de Colores Completa

```
Púrpura Principal: #667eea
Púrpura Oscuro:    #764ba2
Negro Suave:       #333 (títulos)
Gris Medio:        #666 (texto secundario)
Gris Claro:        #999 (footer)
Borde:             #e0e0e0
Fondo Claro:       #f8f9fa
Blanco:            #ffffff
```

## 📝 Código CSS Destacado

```css
/* Botón con gradiente */
button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 13px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

/* Caja de información */
.info-box {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

/* Icono circular */
.success-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}
```
