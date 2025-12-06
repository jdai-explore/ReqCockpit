use tauri::Manager;
use std::process::Command;

#[tauri::command]
fn import_master_spec(project_id: i32, file_path: String) -> Result<usize, String> {
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            "from backend.import_manager import ImportManager; \
             from sqlalchemy import create_engine; \
             engine = create_engine('sqlite:///projects/{}.sqlite'); \
             im = ImportManager(engine); \
             print(im.import_master_spec({}, '{}'))",
            project_id, project_id, file_path
        ))
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        let count_str = String::from_utf8(output.stdout).map_err(|e| e.to_string())?;
        count_str.trim().parse::<usize>().map_err(|e| e.to_string())
    } else {
        Err(String::from_utf8(output.stderr).unwrap_or_else(|_| "Unknown error".to_string()))
    }
}

#[tauri::command]
fn import_supplier_feedback(
    project_id: i32,
    iteration_id_str: String,
    supplier_name: String,
    file_path: String,
) -> Result<usize, String> {
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            "from backend.import_manager import ImportManager; \
             from sqlalchemy import create_engine; \
             engine = create_engine('sqlite:///projects/{}.sqlite'); \
             im = ImportManager(engine); \
             print(im.import_supplier_feedback({}, '{}', '{}', '{}'))",
            project_id, project_id, iteration_id_str, supplier_name, file_path
        ))
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        let count_str = String::from_utf8(output.stdout).map_err(|e| e.to_string())?;
        count_str.trim().parse::<usize>().map_err(|e| e.to_string())
    } else {
        Err(String::from_utf8(output.stderr).unwrap_or_else(|_| "Unknown error".to_string()))
    }
}

#[tauri::command]
fn get_cockpit_data(project_id: i32, iteration_id: i32) -> Result<String, String> {
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            "from backend.cockpit_data_service import CockpitDataService; \
             from sqlalchemy import create_engine; \
             import json; \
             engine = create_engine('sqlite:///projects/{}.sqlite'); \
             cds = CockpitDataService(engine); \
             print(json.dumps(cds.get_cockpit_data({}, {})))",
            project_id, project_id, iteration_id
        ))
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8(output.stdout).map_err(|e| e.to_string())?)
    } else {
        Err(String::from_utf8(output.stderr).unwrap_or_else(|_| "Unknown error".to_string()))
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .invoke_handler(tauri::generate_handler![
        import_master_spec,
        import_supplier_feedback,
#[tauri::command]
fn list_recent_projects(app_handle: tauri::AppHandle) -> Result<String, String> {
    let app_data_dir = app_handle.path_resolver()
        .app_data_dir()
        .ok_or_else(|| "Could not resolve app data directory".to_string())?
        .to_string_lossy()
        .to_string();

    let script_path = app_handle.path_resolver()
        .resolve_resource("backend/main.py")
        .ok_or_else(|| "Could not resolve backend script path".to_string())?
        .to_string_lossy()
        .to_string();

    let output = Command::new("python3")
        .arg(&script_path)
        .arg("list_recent_projects")
        .arg(&app_data_dir)
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8(output.stdout).map_err(|e| e.to_string())?)
    } else {
        Err(String::from_utf8(output.stderr).unwrap_or_else(|_| "Unknown error".to_string()))
    }
}

#[tauri::command(async)]
async fn create_project(app_handle: tauri::AppHandle, name: String, path: String) -> Result<String, String> {
    let app_data_dir = app_handle.path_resolver()
        .app_data_dir()
        .ok_or_else(|| "Could not resolve app data directory".to_string())?
        .to_string_lossy()
        .to_string();

    let script_path = app_handle.path_resolver()
        .resolve_resource("backend/main.py")
        .ok_or_else(|| "Could not resolve backend script path".to_string())?
        .to_string_lossy()
        .to_string();

    let output = Command::new("python3")
        .arg(&script_path)
        .arg("create_project")
        .arg(&app_data_dir)
        .arg(&name)
        .arg(&path)
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8(output.stdout).map_err(|e| e.to_string())?)
    } else {
        Err(String::from_utf8(output.stderr).unwrap_or_else(|_| "Unknown error".to_string()))
    }
}


        get_cockpit_data,
        list_recent_projects,
        create_project
    ])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
