import React from 'react';
import { Box, CssBaseline, AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemText, ListItemButton, ListItemIcon } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import AssistantIcon from '@mui/icons-material/Assistant';
import { useNavigate } from 'react-router-dom';

const drawerWidth = 200;

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [open, setOpen] = React.useState(true);
  const navigate = useNavigate();

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: open ? `calc(100% - ${drawerWidth}px)` : '100%',
          ml: open ? `${drawerWidth}px` : 0,
          transition: 'width 0.2s, margin-left 0.2s',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            PRESENTATION-EVALUATOR
          </Typography>
        </Toolbar>
      </AppBar>
      {/* Sidebar */}
      <Drawer
        variant="persistent"
        open={open}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar>
          <IconButton onClick={handleDrawerToggle}>
            <MenuIcon />
          </IconButton>
        </Toolbar>
        <List>
          <ListItem disablePadding>
            <ListItemButton onClick={() => navigate('/')}> 
              <ListItemIcon>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText primary="Home" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => navigate('/review')}>
              <ListItemIcon>
                <AssistantIcon />
              </ListItemIcon>
              <ListItemText primary="Review" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => navigate('/log')}>
              <ListItemIcon>
                <EqualizerIcon />
              </ListItemIcon>
              <ListItemText primary="Log" />
            </ListItemButton>
          </ListItem>
        </List>
      </Drawer>
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: open ? `calc(100% - ${drawerWidth}px)` : '100%',
          transition: 'width 0.2s',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;