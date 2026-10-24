import gleam/list

pub type Tuning {
  OpenG
  DoubleC
}

pub type ChordQuality {
  Major
  Minor
}

pub type Model {
  Model(tuning: Tuning, selected_root: Int, quality: ChordQuality)
}

pub type Msg {
  SetTuning(Tuning)
  SetRoot(Int)
  SetQuality(ChordQuality)
}

pub fn init() -> Model {
  Model(tuning: OpenG, selected_root: 7, quality: Major)
}

pub fn update(model: Model, msg: Msg) -> Model {
  case msg {
    SetTuning(tuning) -> Model(..model, tuning: tuning)
    SetRoot(root) -> Model(..model, selected_root: modulo12(root))
    SetQuality(quality) -> Model(..model, quality: quality)
  }
}

fn modulo12(value: Int) -> Int {
  let remainder = value % 12
  case remainder < 0 {
    True -> remainder + 12
    False -> remainder
  }
}

// Strings ordered 5th (short drone), 4th, 3rd, 2nd, 1st.
// Pitch classes: C = 0, C# = 1, ..., B = 11.
pub fn open_string_pitch_classes(tuning: Tuning) -> List(Int) {
  case tuning {
    OpenG -> [7, 2, 7, 11, 2]
    DoubleC -> [7, 0, 7, 0, 2]
  }
}

pub fn pitch_class_at(
  tuning: Tuning,
  string_number: Int,
  physical_fret: Int,
) -> Result(Int, Nil) {
  case list.at(open_string_pitch_classes(tuning), 5 - string_number) {
    Ok(open_pitch) -> {
      let start = case string_number {
        5 -> 5
        _ -> 0
      }
      case physical_fret >= start {
        True -> Ok(modulo12(open_pitch + physical_fret - start))
        False -> Error(Nil)
      }
    }
    Error(_) -> Error(Nil)
  }
}

pub fn is_chord_tone(pitch_class: Int, root: Int, quality: ChordQuality) -> Bool {
  let interval = modulo12(pitch_class - root)
  case quality, interval {
    _, 0 -> True
    Major, 4 -> True
    Minor, 3 -> True
    _, 7 -> True
    _, _ -> False
  }
}
