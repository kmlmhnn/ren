# ren

[![Build status](https://ci.appveyor.com/api/projects/status/a45lh7ne89ojttxv?svg=true)](https://ci.appveyor.com/project/kmlmhnn/ren)

**ren** is a bulk file renaming tool.

Renaming files in **ren** is a 4 step process:
  - Open the source directory.
  - Select one or more files to rename.
  - Apply one or more renaming transformations to the selection.
  - Commit the changes made.

### Opening directories

To open a directory, start by pressing **O**, navigate to the desired location in the dialog box that appears, and click **OK**.
The left column should now be populated with the directory contents.

### Selecting files

At any point, the left column shows the current selection.

To filter the entries shown in the left column, press **/**.
A cursor should appear in the lower-left text box.
Type a `key` here and press **Enter**.
The new selection should only contain filenames from the previous selection in which `key` appears as a substring.

To undo the last filter operation and restore the previous selection, press **\\**.

### Applying transformations

The following table shows the transformation commands supported by **ren**.
For commands that take a `key`, the `key` selects a substring within the source filename.


| Command | Requires `key` | Requires `arg` | Description |
| ------- | -------------- | -------------- | ----------- |
| **i** | Yes | Yes | Insert `arg` to the left of the selection |
| **a** | Yes | Yes | Insert `arg` to the right of the selection |
| **I** | No | Yes | Prefix filename with `arg` |
| **A** | No | Yes | Insert `arg` as a filename suffix |
| **c** | Yes | Yes | Replace the selection with `arg` |
| **u** | No | No | Undo last transformation |

For commands that take an `arg`, invoking the command sets the focus on the lower-right text box.
Type an `arg` here and press **Enter** to proceed.

To specify a `key` without triggering a filter, press **/**, type the new `key`, and hit **Escape** instead of **Enter**.

To cancel an unintentionally invoked transformation, press **Escape** while the focus is set on the lower-right text box.

### Committing changes
Hit **M** to commit the changes made to the current selection to disk.
