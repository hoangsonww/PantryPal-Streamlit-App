#!/usr/bin/env bash
set -e

# 1️⃣ Make dotnet folder and enter it
mkdir -p dotnet/src/PantryPal.API
cd dotnet

# 2️⃣ Create csproj with pack metadata
cat > PantryPal.API.csproj << 'EOF'
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net7.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <IsPackable>true</IsPackable>
    <Authors>Son Nguyen</Authors>
    <PackageId>PantryPal.API</PackageId>
    <Version>1.0.0</Version>
    <Description>AI-powered recipe generator backend for PantryPal</Description>
    <PackageTags>recipe;ai;dotnet;api;gemini</PackageTags>
    <RepositoryUrl>https://github.com/hoangsonww/PantryPal-Streamlit-App</RepositoryUrl>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="7.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="7.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="7.0.0" PrivateAssets="all" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.4.0" />
  </ItemGroup>
</Project>
EOF

# 3️⃣ Copy that into src folder
mv PantryPal.API.csproj src/PantryPal.API/

# 4️⃣ Scaffold Program.cs
cat > src/PantryPal.API/Program.cs << 'EOF'
using Microsoft.EntityFrameworkCore;
using PantryPal.API.Data;
using PantryPal.API.Repositories;
using PantryPal.API.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<AppDbContext>(opts =>
    opts.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddScoped<IRecipeRepository, RecipeRepository>();
builder.Services.AddScoped<IRecipeService, RecipeService>();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();
if (app.Environment.IsDevelopment()) { app.UseSwagger(); app.UseSwaggerUI(); }
app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();
app.Run();
EOF

# 5️⃣ Create folder structure
mkdir -p src/PantryPal.API/{Data,Models,Repositories,Services,Controllers}

# 6️⃣ AppDbContext
cat > src/PantryPal.API/Data/AppDbContext.cs << 'EOF'
using Microsoft.EntityFrameworkCore;
using PantryPal.API.Models;

namespace PantryPal.API.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> opts) : base(opts) { }
        public DbSet<Recipe> Recipes => Set<Recipe>();
        public DbSet<Ingredient> Ingredients => Set<Ingredient>();
    }
}
EOF

# 7️⃣ Models
cat > src/PantryPal.API/Models/Ingredient.cs << 'EOF'
namespace PantryPal.API.Models
{
    public class Ingredient
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = default!;
    }
}
EOF

cat > src/PantryPal.API/Models/Recipe.cs << 'EOF'
namespace PantryPal.API.Models
{
    public class Recipe
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = default!;
        public string Instructions { get; set; } = default!;
        public ICollection<Ingredient> Ingredients { get; set; } = new List<Ingredient>();
        public DateTime CreatedAt { get; set; }
    }
}
EOF

# 8️⃣ Repository interfaces & impl
cat > src/PantryPal.API/Repositories/IRecipeRepository.cs << 'EOF'
using PantryPal.API.Models;

namespace PantryPal.API.Repositories
{
    public interface IRecipeRepository
    {
        Task<IEnumerable<Recipe>> GetAllAsync();
        Task<Recipe?> GetByIdAsync(Guid id);
        Task AddAsync(Recipe r);
    }
}
EOF

cat > src/PantryPal.API/Repositories/RecipeRepository.cs << 'EOF'
using Microsoft.EntityFrameworkCore;
using PantryPal.API.Data;
using PantryPal.API.Models;

namespace PantryPal.API.Repositories
{
    public class RecipeRepository : IRecipeRepository
    {
        private readonly AppDbContext _db;
        public RecipeRepository(AppDbContext db) => _db = db;

        public async Task<IEnumerable<Recipe>> GetAllAsync() =>
            await _db.Recipes.Include(r => r.Ingredients).ToListAsync();

        public async Task<Recipe?> GetByIdAsync(Guid id) =>
            await _db.Recipes.Include(r => r.Ingredients).FirstOrDefaultAsync(r => r.Id == id);

        public async Task AddAsync(Recipe r)
        {
            _db.Recipes.Add(r);
            await _db.SaveChangesAsync();
        }
    }
}
EOF

# 9️⃣ Service interfaces & impl
cat > src/PantryPal.API/Services/IRecipeService.cs << 'EOF'
using PantryPal.API.Models;

namespace PantryPal.API.Services
{
    public interface IRecipeService
    {
        Task<Recipe> GenerateAsync(IEnumerable<string> pantry, IEnumerable<string>? prefs);
        Task<IEnumerable<Recipe>> GetHistoryAsync();
    }
}
EOF

cat > src/PantryPal.API/Services/RecipeService.cs << 'EOF'
using PantryPal.API.Models;
using PantryPal.API.Repositories;

namespace PantryPal.API.Services
{
    public class RecipeService : IRecipeService
    {
        private readonly IRecipeRepository _repo;
        public RecipeService(IRecipeRepository repo) => _repo = repo;

        public async Task<Recipe> GenerateAsync(IEnumerable<string> pantry, IEnumerable<string>? prefs)
        {
            // stub: integrate Gemini AI here
            var recipe = new Recipe {
                Id = Guid.NewGuid(),
                Title = "Sample AI Recipe",
                Instructions = "1. Mix ingredients.\n2. Cook.\n3. Serve.",
                CreatedAt = DateTime.UtcNow
            };
            foreach(var i in pantry) recipe.Ingredients.Add(new Ingredient { Id = Guid.NewGuid(), Name = i });
            await _repo.AddAsync(recipe);
            return recipe;
        }

        public Task<IEnumerable<Recipe>> GetHistoryAsync() =>
            _repo.GetAllAsync();
    }
}
EOF

# 🔟 Controller
cat > src/PantryPal.API/Controllers/RecipesController.cs << 'EOF'
using Microsoft.AspNetCore.Mvc;
using PantryPal.API.Models;
using PantryPal.API.Services;

namespace PantryPal.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class RecipesController : ControllerBase
    {
        private readonly IRecipeService _svc;
        public RecipesController(IRecipeService svc) => _svc = svc;

        [HttpPost("generate")]
        public async Task<IActionResult> Generate([FromBody] string[] pantry,
                                                  [FromQuery] string[]? prefs)
        {
            var r = await _svc.GenerateAsync(pantry, prefs);
            return CreatedAtAction(nameof(GetById), new { id = r.Id }, r);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(Guid id) =>
            (await _svc.GetHistoryAsync())
              .FirstOrDefault(r => r.Id == id) is Recipe r
                ? Ok(r)
                : NotFound();

        [HttpGet("history")]
        public async Task<IActionResult> History() =>
            Ok(await _svc.GetHistoryAsync());
    }
}
EOF

# 1️⃣1️⃣ Dockerfile
cat > src/PantryPal.API/Dockerfile << 'EOF'
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /src
COPY ../PantryPal.API.csproj ./
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app
FROM mcr.microsoft.com/dotnet/aspnet:7.0
WORKDIR /app
COPY --from=build /app .
EXPOSE 80
ENTRYPOINT ["dotnet","PantryPal.API.dll"]
EOF

# 1️⃣2️⃣ nuget.config
cat > nuget.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="github" value="https://nuget.pkg.github.com/hoangsonww/index.json" />
  </packageSources>
  <packageSourceCredentials>
    <github>
      <add key="Username" value="hoangsonww" />
      <add key="ClearTextPassword" value="${GH_TOKEN}" />
    </github>
  </packageSourceCredentials>
</configuration>
EOF

echo "✅ Scaffold complete in dotnet/src/PantryPal.API"
echo " • To pack & push (inside Docker):"
echo "   cd dotnet && " \
"docker run --rm -e GH_TOKEN=… -v \$PWD:/ws -w /ws " \
"mcr.microsoft.com/dotnet/sdk:7.0 sh -c \"dotnet pack src/PantryPal.API.csproj -c Release -o artifacts && dotnet nuget push artifacts/*.nupkg --source https://nuget.pkg.github.com/hoangsonww/index.json --api-key \$GH_TOKEN\""
