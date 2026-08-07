// ============================================================
//  Rear-Tracker Case v1 — Raspberry Pi 5 + alert board + camera mount
// ============================================================
//  PART = "base"      -> main enclosure tray (Pi + alert-board standoffs)
//  PART = "lid"        -> vented lid w/ IO + CSI ribbon cutouts
//  PART = "camera"     -> small rear camera bracket (Camera Module 3)
//  PART = "assembly"   -> all three shown together, for a quick look
//
//  Render one part at a time for printing, e.g.:
//     openscad -D 'PART="base"'   -o base.stl   case.scad
//     openscad -D 'PART="lid"'    -o lid.stl    case.scad
//     openscad -D 'PART="camera"' -o camera.stl case.scad
//
//  Notes:
//  - Pi board footprint (85x56mm) and mounting-hole pattern (58x49mm,
//    3.5mm inset) are the standard Pi spec, unchanged since Model B+,
//    so these should be accurate.
//  - Port cutouts are modeled as one generous slot per edge rather
//    than tight per-connector holes, on purpose — verify against the
//    official Pi 5 mechanical drawing (raspberrypi.com) before printing
//    if you want a tighter-fitting result.
//  - Lid is a friction-fit skirt. Fine for a bench test; for something
//    that lives in a car, add a dab of hot glue or two M2 screws once
//    you're happy with the fit — vibration will work a pure friction
//    fit loose over time.
// ============================================================

PART = "assembly";   // "base" | "lid" | "camera" | "assembly"

// ---- Pi 5 board ----
pi_len = 85; pi_wid = 56;
hole_inset = 3.5; hole_span_x = 58; hole_span_y = 49; hole_d = 2.8;
component_h = 17;                 // top-side keepout: HDMI/USB stack + margin

// ---- shell ----
wall = 2.2; floor_h = 2.4; standoff_h = 6;
lid_wall_h = component_h + 3;     // lid skirt depth
fillet_r = 2.5;

// ---- alert board (buzzer / LED / arm-button perfboard) ----
alert_w = 40; alert_d = 30; alert_standoff_h = 5;

// ---- cutouts ----
port_slot_w = pi_len - 24; port_slot_h = 14;
csi_slot_w = 16; csi_slot_h = 6;
vent_n = 9; vent_w = 2; vent_gap = 4.2; vent_len = 26;

// ---- zip-tie mount channels (through the base floor) ----
tie_slot_w = 4; tie_slot_len = 14; tie_spacing = 30;

$fn = 48;

module rounded_box(x, y, z, r) {
    hull()
        for (dx = [r, x - r])
            for (dy = [r, y - r])
                translate([dx, dy, 0]) cylinder(h = z, r = r);
}

outer_x = pi_len + 2*wall + 6;
outer_y = pi_wid + 2*wall + 6;
outer_z = floor_h + standoff_h + 4;

module base() {
    difference() {
        union() {
            difference() {
                rounded_box(outer_x, outer_y, outer_z, fillet_r);
                // hollow interior, open top
                translate([wall, wall, floor_h])
                    cube([outer_x - 2*wall, outer_y - 2*wall, outer_z]);
                // IO port slot (long edge)
                translate([(outer_x - port_slot_w)/2, -1, floor_h + 3])
                    cube([port_slot_w, wall + 2, port_slot_h]);
                // CSI ribbon slot (short edge, toward the camera side)
                translate([-1, outer_y/2 - csi_slot_w/2, floor_h + 2])
                    cube([wall + 2, csi_slot_w, csi_slot_h]);
                // zip-tie channels through the floor
                for (yoff = [-tie_spacing/2, tie_spacing/2])
                    translate([outer_x/2 - tie_slot_len/2, outer_y/2 + yoff - tie_slot_w/2, -1])
                        cube([tie_slot_len, tie_slot_w, floor_h + 2]);
            }
            // Pi mounting standoffs (added back in solid, after hollowing)
            for (dx = [hole_inset, hole_inset + hole_span_x])
                for (dy = [hole_inset, hole_inset + hole_span_y])
                    translate([dx + 3 + wall, dy + 3 + wall, floor_h])
                        cylinder(h = standoff_h, d = 6);
            // alert-board standoffs, tucked in the corner beside the Pi
            for (dx = [0, alert_w - 8])
                for (dy = [0, alert_d - 8])
                    translate([outer_x - alert_w - wall - 6 + dx, wall + 6 + dy, floor_h])
                        cylinder(h = alert_standoff_h, d = 5);
        }
        // Pi screw holes, punched through the standoffs last
        for (dx = [hole_inset, hole_inset + hole_span_x])
            for (dy = [hole_inset, hole_inset + hole_span_y])
                translate([dx + 3 + wall, dy + 3 + wall, -1])
                    cylinder(h = standoff_h + 6, d = hole_d);
    }
}

module lid() {
    difference() {
        rounded_box(outer_x, outer_y, wall, fillet_r);
        // vent slots, roughly above the SoC
        for (i = [0 : vent_n - 1])
            translate([outer_x/2 - (vent_n*vent_gap)/2 + i*vent_gap, outer_y/2 - vent_len/2, -1])
                cube([vent_w, vent_len, wall + 2]);
    }
    // skirt that presses down inside the base tray
    translate([wall + 1.2, wall + 1.2, -lid_wall_h])
        difference() {
            rounded_box(outer_x - 2*wall - 2.4, outer_y - 2*wall - 2.4, lid_wall_h, fillet_r - 1);
            translate([1.4, 1.4, -1])
                rounded_box(outer_x - 2*wall - 5.2, outer_y - 2*wall - 5.2, lid_wall_h + 2, max(fillet_r - 1.5, 0.5));
        }
}

module camera_mount() {
    // Camera Module 3 board is roughly 25x24mm w/ two mounting holes —
    // double check against your specific camera board before drilling tight.
    cam_hole_span = 21; lens_d = 9; plate_t = 3;
    pw = 26 + 12; ph = 26 + 12;
    difference() {
        rounded_box(pw, ph, plate_t, 3);
        translate([pw/2, ph/2, -1]) cylinder(h = plate_t + 2, d = lens_d);
        for (dx = [-cam_hole_span/2, cam_hole_span/2])
            translate([pw/2 + dx, ph/2, -1]) cylinder(h = plate_t + 2, d = 2.4);
        // strap/zip-tie holes for mounting to a window bracket
        for (yoff = [-8, 8])
            translate([pw/2 - 6, ph - 6 + yoff, -1])
                cylinder(h = plate_t + 2, d = 3.2);
    }
}

module assembly_preview() {
    base();
    translate([0, 0, outer_z + 6]) color("SkyBlue", 0.85) lid();
    translate([-(outer_x*0.55), outer_y*0.25, 4]) color("Orange") camera_mount();
}

if (PART == "base") base();
else if (PART == "lid") lid();
else if (PART == "camera") camera_mount();
else assembly_preview();
