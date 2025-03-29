#include <gtk/gtk.h>

void add_child(GtkWidget *parent, GtkBuilder *builder, GObject *child) {
    if (!GTK_IS_WIDGET(parent) || !GTK_IS_WIDGET(child)) {
        g_warning("Parent or child is not a valid GtkWidget.");
        return;
    }

    if (!GTK_IS_BUILDABLE(parent)) {
        g_warning("Parent widget is not a GtkBuildable.");
        return;
    }

    GtkBuildableIface *iface = GTK_BUILDABLE_GET_IFACE(parent);
    if (!iface || !iface->add_child) {
        g_warning("add_child vfunc not found.");
        return;
    }

    iface->add_child(GTK_BUILDABLE(parent), builder, child, "");
}
