!-----------------------------------------------------------------------------------------------
! GRID-DATA: Mapping tool from GIS(.XYZ) data to GRID
!
!        Copyleft 2009-- by Seizo Tanaka (ST3)
!                  and C.H.Lab., University of Notre Dame
!
!   2010.07.07. Prototype 03 moved to ver.1.0
!   2011.01.29. ver.1.2 added LIDAR data on GAP database format
!   2011.01.03. ver.1.2zc added ability to change lidar data units ft/meters and intvert (negaposi) - Zach Cobell
!   2011.03.03. ver.1.3 minute adjustment on WindDirectional part.
!   2011.07.22. ver 1.31 allow multiple smoothing iterations, bugfix for DSIGN must be double
!                   read flagged grid for smoothing - Zach Cobell     
!   2011.10.20. ver 1.32 added -DHIGHMEM for parallel processing - Zach Cobell             
!-----------------------------------------------------------------------------------------------
!
module parameters
      implicit none
      character(len=10),parameter :: cver='1.32'
      double precision, parameter :: flag_ave =-999.d0, flag_hig=-888.d0, flag_ner=-777.d0
      double precision, parameter :: flag_ave2=-950.d0, flag_ave4=-960.d0, flag_ave8=-970.d0
      double precision, parameter :: defval=-9999.d0
      double precision, parameter :: bdepth=1.2d0 ! USCR/ETOPO Border Depth
      double precision, parameter :: gap_multiply_factor=10000.0d0
! Winds
      double precision, parameter :: wind_radius=10.0d0, wind_sigma=6.0d0
end module parameters
!
module griddata
! Grid DATA
      implicit none
      integer :: nelem, nnode
      double precision, allocatable :: xy(:,:), bathy(:)
      integer, allocatable :: nc(:,:)
      character(len=80) :: gridname
    ! Node-Element Table
      integer :: iean_max
      integer, allocatable :: iean(:), nean(:,:)
      double precision :: edge_l_max
      integer, allocatable :: nflag(:), iscale(:)
      integer :: iscale_max
    ! Node Property Record
      character(len=80) :: recordname
      integer, allocatable :: nprec(:), nmrec(:)
end module griddata
!
module lidar_data
      implicit none
! GIS DATA BLOCK Local
      integer :: ngisblock
      character(len=80), allocatable :: gisblockfilename(:)
      integer, allocatable :: ij_nblock(:,:)
      double precision, allocatable :: opoint_block(:,:)
! GIS DATA Global
      integer :: ij_globe(2)
      double precision :: dxglobe(2), opoint_globe(2)
end module lidar_data
!
module section
      implicit none
      integer :: isec, jsec, ij_section(2), imargin(2)
      double precision, allocatable :: opoint_section(:,:,:)
      double precision, allocatable :: gisval(:,:)
end module section
!
module GAPdata
      implicit none
      integer :: igap
      character(len=80) :: GAPname, GAPtable
      integer :: ncol, nrow, idef_val
      double precision :: xllGAP, yllGAP, cellsize
      integer :: iclass
      integer, allocatable :: nclass(:), nclassi(:)
      double precision, allocatable :: vclass(:)
      double precision, allocatable :: wind12(:,:)
end module GAPdata
!
module gridtable
      implicit none
      integer, parameter :: idiv = 1000
      integer, allocatable :: npiece_add(:,:), npiece(:,:), npiece_list(:)
      double precision, allocatable :: xypiece(:,:,:,:), xgs(:,:)
      double precision :: dx(2), xll(2)
      double precision :: gsmax
      integer :: iover
end module gridtable
!
!===============================================================================================
program main
      use parameters, only:cver
      implicit none
      integer :: igrid, imode 
      
      ! File I/O variables
      integer :: i, iargc
      
      logical :: InputFileFound

      character(len=100) :: InputFile
      character(len=1) :: JunkC
      character(len=80) :: TempC
      character(len=10) :: yn
             

      write(6,*) ' GRID DATA Version ',trim(adjustl(cver))
      write(6,*)

      InputFileFound = .FALSE.
      IF(iargc().GT.0)THEN
          I = 0
          DO WHILE ( I < iargc() )
              i = i + 1
              CALL GETARG(I,TempC)
              IF(TempC(1:2).EQ."-I")THEN
                  InputFileFound = .TRUE.
                  i = i + 1
                  CALL GETARG(I,TempC)
                  READ(TempC,'(A)') InputFile
                  write(6,*) ' Input file name: '
                  write(6,*) InputFile
              ENDIF
          ENDDO
      ENDIF

      IF(.NOT.InputFileFound)THEN
          write(6,*) 'Do you want to use an input file? (Y/N)'
          do
            read(5,*) yn
            if( (yn == 'N') .or. (yn == 'n') ) then
                exit
            elseif( (yn == 'Y') .or. (yn == 'y') ) then
                write(6,'(A,$)') "Enter name of input file: "
                read(*,'(A)') InputFile
                write(6,*) ' Input file name: '
                write(6,*) InputFile
                InputFileFound = .TRUE.
                exit
            else
                write(6,*) ' You must input Y or N.; (Y/N)'
            endif
          enddo  
      ENDIF

      IF(InputFileFound)THEN
        open(5, file=trim(InputFile), action="READ", status="old") ! Read input file
        read(5, '(A1)') JunkC ! FOR BEST RESULTS ...
        read(5, '(A1)') JunkC ! 01234567890 ...
      ENDIF

      call output_mode()
!
      write(6,*)
      write(6,*) ' DATABASE TYPE?'
      write(6,*) '   1. Lattice'
      write(6,*) '   2. Unstructured'
      write(6,*)
      write(6,*) '  or Do you want'
      write(6,*)
      write(6,*) '   3. Smoothing Grid'
      read(5,*) igrid
     
      select case(igrid)
        case(1) ! Lattice TYPE Database
          call lattice()
        case(2) ! Unstructured TYPE Database
          call unstructure()
        case(3) ! Smoothing Grid
          call smoothing( 6 )
        case default
          write(6,*) ' You MUST slect 1,2 or 3'
          stop
      end select

      if(InputFileFound) then
        close(5) ! Close input file
      endif
!
end program main
!===============================================================================================
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine lattice()
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      implicit none
      integer :: imode
!
      do
        write(6,*)
        write(6,*) ' Select mode'
        write(6,*) '   1. Bathy. Mapping from LIDAR data (.xyz)'
        write(6,*) '   2. Bathy. Correcting using GAP data'
        write(6,*) '      or Bathy using GAP data format'
        write(6,*) '   3. Bathy. Mapping from USCR data (.xyz)'
        write(6,*) '   4. Bathy. Mapping from ETOPO data (.xyz)'
        write(6,*)
        write(6,*) '   5. Mannings n Mapping form GAP data'
!
        read(5,*) imode
!
        select case (imode)
          case(1,3,4)
            call lidar_map( imode )
            exit
          case(2)
            call correct_lidar_using_GAP( imode )
            exit
          case(5)
            call GAP_map( imode )
            exit
          case default
        end select
      enddo
!
   end subroutine lattice
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine output_mode()
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      implicit none
      integer :: icheck=0
!
!#ifdef demo
!      write(6,*) '***** DEMO MODE'
!      icheck = icheck + 1
!#endif
!#ifdef class
!      write(6,*) '***** CLASS_CHECK MODE'
!      icheck = icheck + 1
!#endif
!#ifdef check
!      write(6,*) '***** DATABASE_CHECK MODE'
!      icheck = icheck + 1
!#endif
!#ifdef cancel
!      write(6,*) 'You must run under the environmental can use #ifdef'
!      stop
!#endif
   end subroutine output_mode
!
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine lidar_map( imode )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata,      only: gridname, recordname
      use lidar_data,    only: ngisblock, gisblockfilename
      implicit none
      integer, intent(in) :: imode
      integer :: i, istrings
      double precision :: dmemory
      character(len=10) :: cjunk, yn
!
      select case (imode)
         case(1)
            open(10,file='LIDAR.list',status='old',action='read')
            write(6,*) '   Now Reading LIDAR.list ......'
         case(3)
            open(10,file='USCR.list',status='old',action='read')
            write(6,*) '   Now Reading USCR.list ......'
         case(4)
            open(10,file='ETOPO.list',status='old',action='read')
            write(6,*) '   Now Reading ETOPO.list ......'
      end select
      read(10,  *  ) dmemory
      read(10,'(a)') gridname
      read(10,'(a)') recordname
      read(10,  *  ) ngisblock
      allocate( gisblockfilename(ngisblock) )
      do i = 1, ngisblock
         read(10,'(a)') gisblockfilename(i)
      enddo
!
      call read14(imode)
      call readnprecord
      select case (imode)
        case(1)
          call read_lidar
        case(3,4)
          call read_USCRETOPO
      end select
      call def_section(dmemory)
      call mapping(imode)
!
      cjunk = gridname(len_trim(gridname)-2:len_trim(gridname))
      if( (cjunk == "grd") .or. (cjunk == "GRD") ) then
         istrings = 3
      else if (cjunk == ".14") then
         istrings = 2
      else
         istrings = 0
      endif
      call outnew14(istrings,imode)
!
      cjunk = recordname(len_trim(recordname)-3:len_trim(recordname))
      if( (cjunk == ".rec") .or. (cjunk == ".REC") ) then
         istrings = 3
      else
         istrings = 0
      endif
      call outnprecord(istrings,imode)
!
   end subroutine lidar_map
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine readnprecord
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata, only: recordname, nnode, nprec, nmrec
      implicit none
      character(len=10) :: yn
      integer :: n
!
      allocate( nprec(nnode), nmrec(nnode) )
      write(6,*) '  Do you read the old record of nodal property? :(Y/N) '
      do
         read(5,*) yn
         if( (yn == 'N') .or. (yn == 'n') ) then
            nprec(:)=0; nmrec(:)=0
            exit
         elseif( (yn == 'Y') .or. (yn == 'y') ) then
            open(15,file=recordname,status='old',action='read')
            read(15,*) n
            if( n /= nnode ) then
              write(6,*) '    You are trying to use a record file do not match the grid.'
              write(6,*) '    System will refresh the record.'
              nprec(:)=0; nmrec(:)=0
            else
              do n = 1, nnode
                read(15,'(2(i1))') nprec(n),nmrec(n)
              enddo
            endif
            close(15)
            exit
         else
            write(6,*) ' You must input Y or N.; (Y/N)'
         endif
      enddo
   end subroutine readnprecord
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine outnprecord(istrings,imode)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata, only: nnode, recordname, nprec, nmrec, xy
      implicit none
      integer, intent(in) :: istrings, imode
      integer :: n
      character(len=120) :: cline
!
      write(cline,'(i1)') imode
      if( istrings /= 0 ) then
         cline = recordname(1:len_trim(recordname)-istrings-1)//trim(cline) &
                    //recordname(len_trim(recordname)-istrings:len_trim(recordname))
      else
         cline = recordname(1:len_trim(recordname))//trim(cline)
      endif
      open(15,file=cline,status='replace',action='write')
      write(15,*) nnode
      do n = 1, nnode
         write(15,'(2(i1))') nprec(n), nmrec(n)
      enddo
      close(15)
   end subroutine outnprecord
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine read14(imode)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use parameters, only: flag_ave, flag_ave2, flag_hig, flag_ner, defval, flag_ave4, flag_ave8
      use griddata
      implicit none
      integer, intent(in) :: imode
      integer :: n, m, i, j, k, nout
      double precision :: dlength, x1, x2, x3, y1, y2, y3
      double precision, parameter :: eps=2.0d0
      character(len=1) :: yn
!
      open(14,file=gridname,status='old',action='read')
!
      write(6,*) ' Reading GRIDDATA'
!
      nout = 0
      read(14,*)
      read(14,*) nelem, nnode
      allocate( xy(2,nnode), bathy(nnode), nc(3,nelem), nflag(nnode),iscale(nnode) )
      do n = 1, nnode
         read(14,*) i, ( xy(k,n), k=1,2 ), bathy(n)
#ifdef demo
!      if( imode==1 ) then
!        bathy(n) = flag_ave2
!      endif
      if( imode==5 ) then
        bathy(n) = flag_ave
      endif
!      if(imode==3) then
!            if( bathy(n) == flag_ave2 ) then
!!               bathy(n) = flag_ave
!               bathy(n) = flag_ave4
!            endif
!      else if( imode==1 ) then
!         bathy(n) = flag_ave2
!      endif
#endif
         if( i /= n )  then
             write(6,*)
             write(6,*) '  Node number is not sequencial', i, n
             write(6,*) '  System will stop.'
             stop
         endif
         call showbar(nelem+nnode, n, nout)
      enddo
      do m = 1, nelem
         read(14,*) i, j, ( nc(k,m), k=1,3 )
         if( i /= m )  then
             write(6,*)
             write(6,*) '  Element number is not sequencial', i, m
             write(6,*) '  System will stop.'
             stop
         endif
         call showbar(nelem+nnode, nnode+m, nout)
      enddo
      write(6,*)
      close(14)
!
      nflag(:) = 0
      iscale(:) = 1
    if( imode == 500 ) then
      bathy(:) = flag_ave
    endif
      do n = 1, nnode
         if(      (dabs(bathy(n)-flag_ave )<=eps) ) then
            nflag(n) = 1
         else if ((dabs(bathy(n)-flag_hig )<=eps) ) then
            nflag(n) = 2
         else if ((dabs(bathy(n)-flag_ner )<=eps) ) then
            nflag(n) = 3
         else if ((dabs(bathy(n)-flag_ave2)<=eps) ) then
            nflag(n) = 4
            iscale(n) = 2
         else if ((dabs(bathy(n)-flag_ave4)<=eps) ) then
            nflag(n) = 4
            iscale(n) = 4
         else if ((dabs(bathy(n)-flag_ave8)<=eps) ) then
            nflag(n) = 4
            iscale(n) = 8
         endif
      enddo
      iscale_max = maxval( iscale(:) )
!
      if( (imode /= 6) .and. (imode /= 2) ) then
        if( SUM(nflag(:)) == 0 ) then
            write(6,*)
            write(6,*) ' ************************************** '
            write(6,*) '   System could not find flaged node. '
            write(6,*) '   System will stop. '
            stop
        endif
      endif
!
!
! Coordinate System Converting Section
      write(6,*) '  Do you want to convert your Grid to UTM Coordinate?; (Y/N)'
      do
         read(5,*) yn
         if( (yn == 'N') .or. (yn == 'n') ) then
            exit
         elseif( (yn == 'Y') .or. (yn == 'y') ) then
               call LatLonToUTM( nnode, xy )
               exit
         else
               write(6,*) ' You must input Y or N.; (Y/N)'
         endif
      enddo
!
! Make Table of Elements around "a Node"
      iean_max = 10
      allocate( iean(nnode), nean(nnode,iean_max) )
      do
      iean(:) = 0
         k = 0
         Element_loop: do m = 1, nelem 
            do i = 1, 3
               iean(nc(i,m)) = iean(nc(i,m)) + 1
               if( iean(nc(i,m)) > iean_max ) then
                   deallocate( nean )
                   iean_max = iean_max + 5
                   allocate( nean(nnode,iean_max) )
                   k = 1
                   exit Element_loop
               endif
               nean(nc(i,m),iean(nc(i,m))) = m
            enddo
         enddo Element_loop
         if( k == 0 ) exit
      enddo
!
   end subroutine read14
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine read_lidar
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use lidar_data
      use griddata, only: nnode, nelem, xy, nc, edge_l_max, iscale_max
      implicit none
      integer :: i, j, n, m, istatus, icount
      integer :: ix, iy
      integer :: ingis
!
      double precision :: x, y, xmax, xmin, ymax, ymin, dx, dy, xn
      double precision :: gxmax, gxmin, gymax, gymin
      double precision, parameter :: eps=1.0d-06
      double precision, allocatable :: dxblock(:,:)
      double precision, allocatable :: nprop(:)
      double precision :: dlength, x1, x2, x3, y1, y2, y3
!
      gxmax = maxval(xy(1,1:nnode))
      gxmin = minval(xy(1,1:nnode))
      gymax = maxval(xy(2,1:nnode))
      gymin = minval(xy(2,1:nnode))
      write(6,*) gxmax, gymax
      write(6,*) gxmin, gymin
!
! Memory Dynamic Allocation
      allocate ( ij_nblock(2,ngisblock), dxblock(2,ngisblock), opoint_block(2,ngisblock) )
!
!#ifdef check
!      open(30,file='Lidar.pt')
!#endif
      ingis = 0
      do i = 1, ngisblock
         open(100+i,file=gisblockfilename(i),status='old',action='read')
       !Set Initials
         read(100+i,*,iostat=istatus) x, y
         xmax = x; xmin = x; ymax = y; ymin = y
         dx = x; dy = y; xn = x
         ix = 0  ; iy = 0
       !to Find the REGULAR GRID SIZE of GIS DATA
         do
            read(100+i,*,iostat=istatus) x, y
            if( istatus < 0 ) then
                write(6,*) '  At least, System require 2x2 GIS data set'
                write(6,*) '  System will stop.', i, istatus
                stop
            endif
            xmax = dmax1(xmax,x); xmin = dmin1(xmin,x)
            ymax = dmax1(ymax,y); ymin = dmin1(ymin,y)
            if( ix /= 1 ) then
               if( dabs(dx-x) >= eps  )then
                  dx = x - dx
                  ix = 1
               else
                  dx = x
               endif
            endif
            if( iy /= 1 ) then
               if( (dabs(xn-x)<=eps) .and. (dabs(dy-y)>=eps) )then
                  dy = y - dy
                  iy = 1
               else
                  dy = y
               endif
            endif
            xn = x
            if( ix*iy /= 0 ) exit
         enddo
       ! Standard
         do
            read(100+i,*,iostat=istatus) x, y
            if( istatus < 0 ) exit
            xmax = dmax1(xmax,x); xmin = dmin1(xmin,x)
            ymax = dmax1(ymax,y); ymin = dmin1(ymin,y)
         enddo
         close(100+i)
!#ifdef check
!         write(30,*) xmin, ymax
!         write(30,*) xmin, ymin
!         write(30,*) xmax, ymin
!         write(30,*) xmax, ymax
!         write(30,*) xmin, ymax
!         write(30,*)
!         write(30,*) xmax, ymax
!         write(30,*) xmin, ymin
!         write(30,*)
!#endif
!
       if( (gxmin>xmax) .or. (gxmax<xmin) .or. (gymin>ymax) .or. (gymax<ymin) ) cycle
       ingis = ingis + 1
       gisblockfilename(ingis) = gisblockfilename(i)
       
       ! define the start point and num of row/col
         opoint_block(1,ingis) = xmin
         opoint_block(2,ingis) = ymax
         ij_nblock(1,ingis) = nint(  (xmax-xmin) / dx ) + 1
         ij_nblock(2,ingis) = nint( -(ymax-ymin) / dy ) + 1
         dxblock(1,ingis) = dx
         dxblock(2,ingis) = dy
         write(6,'(a,i6)') gisblockfilename(ingis)(1:len_trim(gisblockfilename(ingis))), ingis
         write(6,*) opoint_block(1,ingis), opoint_block(2,ingis)
         write(6,*) xmax, ymin
      enddo
      write(6,*) ngisblock, ingis, 'TAIZO'
      ngisblock = ingis
!#ifdef check
!      close(30)
!#endif
!
!   check the grid size of each block
      dx = dxblock(1,1); dy = dxblock(2,1)
      do i = 1, ngisblock
         if((dabs(dx-dxblock(1,i)) > eps) .or. (dabs(dy-dxblock(2,i)) > eps) ) then
             write(6,*) '   Block',i,'has different nodal interval'
             write(6,*) '   dx:',dx,'/=', dxblock(1,i)
             write(6,*) '   dy:',dy,'/=', dxblock(2,i)
             stop
         endif
      enddo
!
! Make the global gis area
      xmin = opoint_block(1,1); ymax = opoint_block(2,1)
      xmax = opoint_block(1,1) + dx * (ij_nblock(1,1) - 1)
      ymin = opoint_block(2,1) + dy * (ij_nblock(2,1) - 1)
      do i = 1, ngisblock
         x = opoint_block(1,i); y = opoint_block(2,i)
         xmin = dmin1(x,xmin); ymax = dmax1(y,ymax)
         x = opoint_block(1,i) + dx * (ij_nblock(1,i) - 1)
         y = opoint_block(2,i) + dy * (ij_nblock(2,i) - 1)
         xmax = dmax1(x,xmax); ymin = dmin1(y,ymin)
      enddo
      opoint_globe(1) = xmin
      opoint_globe(2) = ymax
      ij_globe(1) = nint(  (xmax-xmin) / dx ) + 1
      ij_globe(2) = nint( -(ymax-ymin) / dy ) + 1
      dxglobe(1) = dx; dxglobe(2) = dy
!
!
         write(6,*)
         write(6,*) '*Global GIS DATA AREA INFO.'
         write(6,*) '  Start Point:',opoint_globe(1), opoint_globe(2)
         write(6,*) '  End   Point:',xmax, ymin
         write(6,*) '  (i,j):      ',ij_globe(1), ij_globe(2)
         write(6,*) '  Grid size:  ',dxglobe(1), dxglobe(2)
!
       allocate( nprop(nnode) )
       nprop(:) = 0
       xmin = ( xmin + xmax ) * 0.5d0
       ymin = ( ymin + ymax ) * 0.5d0
       do n = 1, nnode
          if( (dabs(xy(1,n)-xmin) <= dabs(dx)*dble(ij_globe(1))*0.5d0) &
          .and.(dabs(xy(2,n)-ymin) <= dabs(dy)*dble(ij_globe(2))*0.5d0))  then
               nprop(n) = 1
          endif
       enddo
! Find the longest edge length for the Margin of Sub-GIS-grid near GIS area
       edge_l_max = 0.0d0
       do m = 1, nelem
          j = 0
          do i = 1, 3
             j = j + nprop(nc(i,m))
          enddo
          if (j == 0 ) cycle
          x1 = xy(1,nc(1,m)); y1 = xy(2,nc(1,m))
          x2 = xy(1,nc(2,m)); y2 = xy(2,nc(2,m))
          x3 = xy(1,nc(3,m)); y3 = xy(2,nc(3,m))
          dlength = dsqrt( (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
          edge_l_max = dmax1(edge_l_max,dlength)
          dlength = dsqrt( (x2-x3)*(x2-x3) + (y2-y3)*(y2-y3))
          edge_l_max = dmax1(edge_l_max,dlength)
          dlength = dsqrt( (x3-x1)*(x3-x1) + (y3-y1)*(y3-y1))
          edge_l_max = dmax1(edge_l_max,dlength)
       enddo
       write(6,*) sum(nprop(:)), edge_l_max, edge_l_max*dble(iscale_max)
       edge_l_max = edge_l_max*dble(iscale_max)
          
!
      deallocate( dxblock, nprop )
!
   end subroutine read_lidar
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine read_USCRETOPO
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use lidar_data
      use griddata, only: nnode, nelem, xy, nc, edge_l_max, iscale_max
      implicit none
      integer :: i, j, n, m, istatus, icount
      integer :: ix, iy
!
      double precision :: x, y, xmax, xmin, ymax, ymin, dx, dy, yn
      double precision, parameter :: eps=1.0d-06
      double precision, allocatable :: dxblock(:,:)
      double precision, allocatable :: nprop(:)
      double precision :: dlength, x1, x2, x3, y1, y2, y3
!
! Memory Dynamic Allocation
      allocate ( ij_nblock(2,ngisblock), dxblock(2,ngisblock), opoint_block(2,ngisblock) )
!
!#ifdef check
!      open(30,file='USCRETOPO.pt')
!#endif

      do i = 1, ngisblock
         open(100+i,file=gisblockfilename(i),status='old',action='read')
       !Set Initials
         read(100+i,*,iostat=istatus) x, y
         xmax = x; xmin = x; ymax = y; ymin = y
         dx = x; dy = y; yn = y
         ix = 0  ; iy = 0
       !to Find the REGULAR GRID SIZE of GIS DATA
         do
            read(100+i,*,iostat=istatus) x, y
            if( istatus < 0 ) then
                write(6,*) '  At least, System require 2x2 GIS data set'
                write(6,*) '  System will stop.', i, istatus
                stop
            endif
            xmax = dmax1(xmax,x); xmin = dmin1(xmin,x)
            ymax = dmax1(ymax,y); ymin = dmin1(ymin,y)
            if( ix /= 1 ) then
               if( (dabs(yn-y) <= eps) .and. (dabs(dx-x) >= eps)  )then
                  dx = x - dx
                  ix = 1
               else
                  dx = x
               endif
            endif
            if( iy /= 1 ) then
               if( dabs(dy-y)>=eps )then
                  dy = y - dy
                  iy = 1
               else
                  dy = y
               endif
            endif
            yn = y
            if( ix*iy /= 0 ) exit
         enddo
       ! Standard
         do
            read(100+i,*,iostat=istatus) x, y
            if( istatus < 0 ) exit
            xmax = dmax1(xmax,x); xmin = dmin1(xmin,x)
            ymax = dmax1(ymax,y); ymin = dmin1(ymin,y)
         enddo
         close(100+i)
!#ifdef check
!         write(30,*) xmin, ymax
!         write(30,*) xmin, ymin
!         write(30,*) xmax, ymin
!         write(30,*) xmax, ymax
!         write(30,*) xmin, ymax
!         write(30,*)
!         write(30,*) xmax, ymax
!         write(30,*) xmin, ymin
!         write(30,*)
!#endif
!
       ! define the start point and num of row/col
         opoint_block(1,i) = xmin
         opoint_block(2,i) = ymax
         ij_nblock(1,i) = nint(  (xmax-xmin) / dx ) + 1
         ij_nblock(2,i) = nint( -(ymax-ymin) / dy ) + 1
         dxblock(1,i) = dx
         dxblock(2,i) = dy
         write(6,'(a,i6)') gisblockfilename(i)(1:len_trim(gisblockfilename(i))), i
         write(6,*) opoint_block(1,i), opoint_block(2,i)
         write(6,*) xmax, ymin
!         write(6,*) ij_nblock(1,i), ij_nblock(2,i)
!         write(6,*) dxblock(1,i), dxblock(2,i)
      enddo
!#ifdef check
!      close(30)
!#endif
!
!   check the grid size of each block
      dx = dxblock(1,1); dy = dxblock(2,1)
      do i = 1, ngisblock
         if((dabs(dx-dxblock(1,i)) > eps) .or. (dabs(dy-dxblock(2,i)) > eps) ) then
             write(6,*) '   Block',i,'has different grid size'
             write(6,*) dx, dxblock(1,i)
             write(6,*) dy, dxblock(2,i)
             stop
         endif
      enddo
!
! Make the global gis area
      xmin = opoint_block(1,1); ymax = opoint_block(2,1)
      xmax = opoint_block(1,1) + dx * (ij_nblock(1,1) - 1)
      ymin = opoint_block(2,1) + dy * (ij_nblock(2,1) - 1)
      do i = 1, ngisblock
         x = opoint_block(1,i); y = opoint_block(2,i)
         xmin = dmin1(x,xmin); ymax = dmax1(y,ymax)
         x = opoint_block(1,i) + dx * (ij_nblock(1,i) - 1)
         y = opoint_block(2,i) + dy * (ij_nblock(2,i) - 1)
         xmax = dmax1(x,xmax); ymin = dmin1(y,ymin)
      enddo
      opoint_globe(1) = xmin
      opoint_globe(2) = ymax
      ij_globe(1) = nint(  (xmax-xmin) / dx ) + 1
      ij_globe(2) = nint( -(ymax-ymin) / dy ) + 1
      dxglobe(1) = dx; dxglobe(2) = dy
!
!
         write(6,*)
         write(6,*) '*Global GIS DATA AREA INFO.'
         write(6,*) '  Start Point:',opoint_globe(1), opoint_globe(2)
         write(6,*) '  End   Point:',xmax, ymin
         write(6,*) '  (i,j):      ',ij_globe(1), ij_globe(2)
         write(6,*) '  Grid size:  ',dxglobe(1), dxglobe(2)
!
       allocate( nprop(nnode) )
       nprop(:) = 0
       xmin = ( xmin + xmax ) * 0.5d0
       ymin = ( ymin + ymax ) * 0.5d0
       do n = 1, nnode
          if( (dabs(xy(1,n)-xmin) <= dabs(dx)*dble(ij_globe(1))*0.5d0) &
          .and.(dabs(xy(2,n)-ymin) <= dabs(dy)*dble(ij_globe(2))*0.5d0))  then
               nprop(n) = 1
          endif
       enddo
! Find the longest edge length for the Margin of Sub-GIS-grid near GIS area
       edge_l_max = 0.0d0
       do m = 1, nelem
          j = 0
          do i = 1, 3
             j = j + nprop(nc(i,m))
          enddo
          if (j == 0 ) cycle
          x1 = xy(1,nc(1,m)); y1 = xy(2,nc(1,m))
          x2 = xy(1,nc(2,m)); y2 = xy(2,nc(2,m))
          x3 = xy(1,nc(3,m)); y3 = xy(2,nc(3,m))
          dlength = dsqrt( (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
          edge_l_max = dmax1(edge_l_max,dlength)
          dlength = dsqrt( (x2-x3)*(x2-x3) + (y2-y3)*(y2-y3))
          edge_l_max = dmax1(edge_l_max,dlength)
          dlength = dsqrt( (x3-x1)*(x3-x1) + (y3-y1)*(y3-y1))
          edge_l_max = dmax1(edge_l_max,dlength)
       enddo
       write(6,*) sum(nprop(:)), edge_l_max, edge_l_max*dble(iscale_max)
       edge_l_max = edge_l_max*dble(iscale_max)
          
!
      deallocate( dxblock, nprop )
!
   end subroutine read_USCRETOPO
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine def_section(dmemory)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata,       only: nnode, nelem, edge_l_max
      use lidar_data,     only: ij_globe, opoint_globe, dxglobe
      use section
      implicit none
      double precision, intent(in) :: dmemory
      double precision :: dmem_grid, dmem_globe, dmem
      integer :: ix, iy, i, j, jx, jy, jjx, jjy
      integer, parameter :: itimes = 2
!
      dmem_grid = nnode * 8 * 3  &  ! x,y,bathy data Double(8 Byte)
                + nelem * 4 * 3     ! node connection in element Int(4 Byte)
      dmem_grid = dmem_grid / (10 ** (6))
      write(6,*)
      write(6,*) '   Now Memory was used for Finite Element Grid:'
      write(6,*)     dmem_grid,'[MB]'
      dmem_globe = dble(ij_globe(1)) * 1.0d-03  * dble(ij_globe(2)) * 1.0d-03 * 8.0d0 
      write(6,*) '   Global GIS data table require another:'
      write(6,*)     dmem_globe,'[MB]'
      dmem_globe = dmemory - dmem_grid
      if( dmem_globe < 0.0d0 ) dmem_globe=dmemory
      ix = ij_globe(1)
      iy = ij_globe(2)
      i = 0
      jx = 0; jy = 0
      jjx = (int( edge_l_max / dabs(dxglobe(1)) ) + 1) * itimes
      jjy = (int( edge_l_max / dabs(dxglobe(2)) ) + 1) * itimes
      do
      i = i + 1
          if ( dble(ix+jjx*2)*dble(iy+jjy*2)*8.0d-6 > dmem_globe ) then
               if( ix >= iy ) then
                   ix = int( dble(ix)/2.0d0 ) + 1
                   jx = jx + 1
               else
                   iy = int( dble(iy)/2.0d0 ) + 1
                   jy = jy + 1
               endif
               if( (ix==1) .and. (iy==1) ) exit
          else
             exit
          endif
      enddo
      write(6,*) dmem_globe, dble(ix)*dble(iy)*8.0d-6, jx, jy
!      write(6,*) i, ix, iy, 2**jx, 2**jy
      write(6,*) ' Global GIS DATA is divided to ',(2**jx)*(2**jy),'sectoions'
      isec = 2 **jx; jsec = 2 ** jy
      allocate ( opoint_section(2,isec,jsec) )
      jx = (int( edge_l_max / dabs(dxglobe(1)) ) + 1) * itimes
      jy = (int( edge_l_max / dabs(dxglobe(2)) ) + 1) * itimes
      ij_section(1) = ix + jx * 2
      ij_section(2) = iy + jy * 2
      write(6,*) ij_section(1), ij_section(2), jx, jy
      do i = 1, isec
         do j = 1, jsec
            opoint_section(1,i,j) = opoint_globe(1) + ix * dxglobe(1)*(i-1) - dxglobe(1) * jx
            opoint_section(2,i,j) = opoint_globe(2) + iy * dxglobe(2)*(j-1) - dxglobe(2) * jy
         enddo
      enddo
      write(6,*) ' Try to secure the gissection workspace!'
      allocate( gisval(ij_section(1),ij_section(2)))
      write(6,*) ' Success!'
      imargin(1) = jx; imargin(2) = jy
!
   end subroutine def_section
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine mapping(imode)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use parameters
      use griddata
      use lidar_data
      use section
      implicit none
!
      integer, intent(in) :: imode
      integer :: is, js, i, j, ib, k, n, m, ne
      integer :: istatus, isect, nout
      integer :: istart, iend, jstart, jend
      double precision :: xmin_sec, xmax_sec, ymin_sec, ymax_sec
      double precision :: xmin,  xmax,  ymin,  ymax, ddx, ddy
      double precision :: x, y, value
      character(len=20) :: c
!
      double precision, parameter :: ft=0.3048 ![m]
!
      integer :: negaposi, nunit
      double precision :: times
!
      write(6,*) '  Input paremeter to convert for GRID '
      write(6,*) '       Nega-Posi: (if you want to convert, please input -1)'
      read(5,*) negaposi
      write(6,*)
      write(6,*) '       Do you want to convert the unit of database value?'
      write(6,*) '          0. No Change'
      write(6,*) '          1. Meter to Feet'
      write(6,*) '          2. Feet to Meter'
      read(5,*) nunit
!
      select case (nunit)
         case(0)
            times = dble(negaposi)
         case(1)
            times = dble(negaposi) / ft
         case(2)
            times = dble(negaposi) * ft
         case default
            times = dble(negaposi)
      end select
!
!!! Moddify nflag for mode 3 & 4
      if( imode == 3 ) then
         do n = 1, nnode
            if( nprec(n) == 0 ) cycle
!            if( nprec(n) /= 2 ) cycle
              nflag(n) = nmrec(n)
              iscale(n) = 1
            if( nmrec(n) == 4 ) then
               nflag(n) = 4
               iscale(n) = 2
            else if (nmrec(n) == 5) then
               nflag(n) = 4
               iscale(n) = 4
            else if (nmrec(n) == 7) then
               nflag(n) = 4
               iscale(n) = 8
            endif
         enddo
!      else if ( imode == 4 ) then
!         do n = 1, nnode
!            if( nprec(n) /= 2 ) cycle
!              nflag(n) = nmrec(n)
!              iscale(n) = 1
!            if( nmrec(n) == 4 ) then
!               nflag(n) = 4
!               iscale(n) = 2
!            else if (nmrec(n) == 5) then
!               nflag(n) = 4
!               iscale(n) = 4
!            else if (nmrec(n) == 7) then
!               nflag(n) = 4
!               iscale(n) = 8
!            endif
!         enddo
      endif
!
!#ifdef check
!      open(30,file='section.pt')
!#endif
! MAPPING LOOP
      isect = 0
      do is = 1, isec
         do js = 1, jsec
            isect= isect + 1
            write(c,*) isect
            write(6,'(a)') '   Lighting on Section.'// adjustl(trim(c))
            gisval(:,:) = defval
            xmin_sec = opoint_section(1,is,js)
            xmax_sec = opoint_section(1,is,js) + (ij_section(1)-1) * dxglobe(1)
            ymax_sec = opoint_section(2,is,js)
            ymin_sec = opoint_section(2,is,js) + (ij_section(2)-1) * dxglobe(2)

!#ifdef check
!            write(30,*) xmin_sec,ymax_sec
!            write(30,*) xmin_sec,ymin_sec
!            write(30,*) xmax_sec,ymin_sec
!            write(30,*) xmax_sec,ymax_sec
!            write(30,*) xmin_sec,ymax_sec
!            write(30,*)
!#endif
!
!        RE-CONSTRUCT GIS DATA ON SECTION
            write(6,'(a)') '    Re-constract GIS data on Section'
            nout = 0
            do ib = 1, ngisblock
               call showbar(ngisblock, ib, nout)
               xmin = opoint_block(1,ib)
               xmax = opoint_block(1,ib) + (ij_nblock(1,ib)-1) * dxglobe(1)
               ymax = opoint_block(2,ib)
               ymin = opoint_block(2,ib) + (ij_nblock(2,ib)-1) * dxglobe(2)
             if( (xmin > xmax_sec) .or. ( xmax < xmin_sec ) &
                .or. (ymin > ymax_sec) .or. (ymax < ymin_sec ) ) cycle
               open(100,file=gisblockfilename(ib),status='old',action='read')
               do 
                  read(100,*,iostat=istatus) x, y, value
                  if( istatus < 0 ) exit
                  i = nint(( x - (opoint_section(1,is,js) )) / dxglobe(1)) + 1
                  j = nint(( y - (opoint_section(2,is,js) )) / dxglobe(2)) + 1
                  if( ( i >= 1 ) .and. ( i <= ij_section(1)) .and. &
                      ( j >= 1 ) .and. ( j <= ij_section(2)) ) then
                      gisval(i,j) = value
                  endif
               enddo
               close(100)
            enddo
            write(6,*) 
!
            write(6,'(a)') '    Mapping to Grid Node'
            nout = 0
            Node_loop: do n = 1, nnode
               call showbar(nnode, n, nout)
               if( nflag(n) == 0 ) cycle
               xmin = xy(1,n); xmax = xy(1,n)
               ymin = xy(2,n); ymax = xy(2,n)
               do ne = 1, iean(n)
                  m = nean(n,ne)
                  do k = 1, 3
                     xmin = dmin1(xmin,xy(1,nc(k,m)))
                     xmax = dmax1(xmax,xy(1,nc(k,m)))
                     ymin = dmin1(ymin,xy(2,nc(k,m)))
                     ymax = dmax1(ymax,xy(2,nc(k,m)))
                  enddo
               enddo
!           nflag(n)==4 is Averaging in Twice (or more) Grid scale
               if( nflag(n) == 4 ) then
                   ddx = (xmax - xmin) * 0.5d0
                   ddy = (ymax - ymin) * 0.5d0
                   xmin = xmin - ddx * dble(iscale(n)-1)
                   xmax = xmax + ddx * dble(iscale(n)-1)
                   ymin = ymin - ddy * dble(iscale(n)-1)
                   ymax = ymax + ddy * dble(iscale(n)-1)
               endif
!
               if( (xmin < xmin_sec) .or. ( xmax > xmax_sec ) &
                  .or. (ymin < ymin_sec) .or. (ymax > ymax_sec ) ) cycle
         !  nflag(n)==3 is Nearest
               if( nflag(n) == 3 ) then
                   i = nint( ( xy(1,n) - opoint_section(1,is,js) ) / dxglobe(1) ) + 1
                   j = nint( ( xy(2,n) - opoint_section(2,is,js) ) / dxglobe(2) ) + 1
                   if( gisval(i,j) == defval ) cycle
                   if( (imode == 3) .or. (imode == 4) ) then
                      if( times*gisval(i,j) < bdepth ) cycle
                      if( (imode==4) .and. (nprec(n)==3) ) cycle
                   endif
                   bathy(n) = times * gisval(i,j)
                   nflag(n) = 0
                   nprec(n) = imode; nmrec(n) = 3
                   cycle
               endif
                   
            ! Define grid size
               xmin = xy(1,n); xmax = xy(1,n)
               ymin = xy(2,n); ymax = xy(2,n)
               do ne = 1, iean(n)
                  m = nean(n,ne)
                  x = 0.0d0; y = 0.0d0
                  do k = 1, 3
                     x = x + xy(1,nc(k,m))
                     y = y + xy(2,nc(k,m))
                  enddo
                     x = x / 3.0d0; y = y / 3.0d0
                     xmin = dmin1(xmin,x)
                     xmax = dmax1(xmax,x)
                     ymin = dmin1(ymin,y)
                     ymax = dmax1(ymax,y)
               enddo
         !  nflag(n)==4 is Averaging in Twice (or more) Grid scale
               if( nflag(n) == 4 ) then
                   ddx = (xmax - xmin) * 0.5d0
                   ddy = (ymax - ymin) * 0.5d0
                   xmin = xmin - ddx * dble(iscale(n)-1)
                   xmax = xmax + ddx * dble(iscale(n)-1)
                   ymin = ymin - ddy * dble(iscale(n)-1)
               endif
!
                   istart = nint( ( xmin - opoint_section(1,is,js) ) / dxglobe(1) ) + 1
                   jstart = nint( ( ymax - opoint_section(2,is,js) ) / dxglobe(2) ) + 1
                   iend   = nint( ( xmax - opoint_section(1,is,js) ) / dxglobe(1) ) + 1
                   jend   = nint( ( ymin - opoint_section(2,is,js) ) / dxglobe(2) ) + 1
!

               if ( (nflag(n)==1) .or. (nflag(n)==4) ) then
!       Average
                   k = 0
                   value = 0.0d0
                   do i = istart, iend
                      do j = jstart, jend
                         if( gisval(i,j) == defval ) cycle
                         value = value + gisval(i,j)
                         k = k + 1
                      enddo
                   enddo
                   if( k /= 0 ) then
                      value = times * value / dble(k)
                      if( (imode == 3) .or. (imode == 4) ) then
                         if( value < bdepth ) cycle
                         if( (imode==4) .and. (nprec(n)==3) ) cycle
                      endif
                      if( iscale(n) == 1 ) then
                         nprec(n) = imode; nmrec(n) = 1
                      elseif( iscale(n) == 2 ) then
                         nprec(n) = imode; nmrec(n) = 4
                      elseif( iscale(n) == 4 ) then
                         nprec(n) = imode; nmrec(n) = 5
                      elseif( iscale(n) == 8 ) then
                         nprec(n) = imode; nmrec(n) = 7
                      endif
                      bathy(n) = value
                      nflag(n) = 0
                   endif
               else if ( nflag(n) == 2 ) then
!      Highest
                   value = times * gisval(istart,jstart)
                   k = 0
                   do i = istart, iend
                      do j = jstart, jend
                         if( gisval(i,j) == defval ) cycle
                         value = dmin1(value, times * gisval(i,j))
                         k = k + 1
                      enddo
                   enddo
                   if( k /= 0 ) then
                      if( (imode == 3) .or. (imode == 4) ) then
                         if( value < bdepth ) cycle
                         if( (imode==4) .and. (nprec(n)==3) ) cycle
                      endif
                      bathy(n) = value
                      nflag(n) = 0
                      nprec(n) = imode; nmrec(n) = 2
                    endif
               endif
            enddo Node_loop
            write(6,*) 
         enddo
      enddo
!#ifdef check
!      close(30)
!#endif
!
   end subroutine mapping
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine outnew14(istrings,imode)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata, only: nnode, nelem, bathy, gridname
!
      implicit none
      integer, intent(in) :: imode, istrings
      character(len=120) :: cline
      character(len=40)  :: c(3)
      integer :: i, j, k, l, m, n
!
      open(14, file=gridname,status='old',action='read')
      if( imode >= 500 ) then
         write(cline,'(i3.3,a)') imode,'w'
      else
         write(cline,'(i1)') imode
      endif
      if( istrings /= 0 ) then
         cline = gridname(1:len_trim(gridname)-istrings-1)//trim(cline) &
                    //gridname(len_trim(gridname)-istrings:len_trim(gridname))
      else
         cline = gridname(1:len_trim(gridname))//trim(cline)
      endif
      write(6,*)cline
      open(140,file=cline,status='replace',action='write')
!
      read(  14,'(a)') cline                         !GRIDNAME
      write(140,'(a)') cline(1:len_trim(cline))      !GRIDNAME
      read(  14,'(a)') cline                         ! NE, NP
      write(140,'(a)') cline(1:len_trim(cline))
      do n = 1, nnode                                ! NODE Position
         read(  14,* ) c(1), c(2), c(3)
         write(140,'(3(x,a),f17.8)') (trim(c(i)), i=1,3), bathy(n)
!         write(140,'(a,f17.8)') cline(1:len_trim(cline)), bathy(n)
      enddo
      do m = 1, nelem                                ! Elements node connectivity
         read(  14,'(a)') cline                      
         write(140,'(a)') cline(1:len_trim(cline))
      enddo
!
!B.C
      do l = 1, 2
         read(  14,'(a)') cline                         !NOPE(l=1),  NBOU(l=2)
         read(cline,*) n
         write(140,'(a)') cline(1:len_trim(cline))
         read(  14,'(a)') cline                         !NETA(l=1),  NVEL(l=2)
         write(140,'(a)') cline(1:len_trim(cline))
         do k = 1, n
            read(  14,'(a)') cline                      !NVDLL(l=1), NVELL(l=2)
            read(cline,*) i
            write(140,'(a)') cline(1:len_trim(cline))
            do j = 1, i
               read(  14,'(a)') cline                   !NBDV(l=1),  NBVV(l=2)
               write(140,'(a)') cline(1:len_trim(cline))
            enddo
         enddo
      enddo
      close(14)
      close(140)
         
   end subroutine outnew14
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine LatLonToUTM ( nnode, xy )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      implicit none
      integer, intent(in) :: nnode
      double precision, intent(inout) :: xy(2,nnode)
!
      double precision :: dlat, dlon, rlat, rlon
      double precision :: x, y
      double precision, parameter :: UTMScaleFactor=0.9996d0
!
      integer :: ihsys, n
      double precision :: a, b
!
      double precision :: pi
      double precision :: dn, salpha, sbeta, sgamma, sdelta, sepsilon, slength
      integer :: zone
      double precision :: cmeridian
      double precision :: sep2, snu2, sN, t, t2, tmp
      double precision :: sl, sl3coef,sl4coef,sl5coef,sl6coef,sl7coef,sl8coef

!
      do 
         write(6,*) ' Select Horizontal System;'
         write(6,*) '     1. GRS80'
         write(6,*) '     2. NAD83/WGS84'
         write(6,*) '     3. WGS72'
         read(5,*) ihsys
         select case(ihsys)
            case(1)
               a=6378137.d0      ! Equatorial Radius
               b=6356752.3141d0  ! Polar Radius
               exit
            case(2)
               a=6378137.d0      ! Equatorial Radius
               b=6356752.3142d0  ! Polar Radius
              !b=6356752.3140d0  ! Polar Radius
               exit
            case(3)
               a=6378135.d0      ! Equatorial Radius
               b=6356750.5000d0  ! Polar Radius
               exit
            case default
               cycle
         end select
      enddo
         write(6,*) ' Input the UTM Zone Number:'
         read(5,*) zone
!
         pi = dacos(-1.0d0)
      do n = 1, nnode
         dlon = xy(1,n)
         dlat = xy(2,n)
         rlat = dlat * pi / 180.0d0
         rlon = dlon * pi / 180.0d0
         dn = (a-b) / (a+b)
         salpha = ((a+b)/2.d0) * ( 1.d0 + dn**(2)/4.d0 + dn**(4)/ 64.d0 )
         sbeta = ( -3.d0*dn/2.d0 ) + ( 9.d0*dn**(3)/16.d0 ) + (-3.d0*dn**(5)/32.d0)
         sgamma = ( 15.d0*dn**2)/16.d0 - (15.d0*dn**(4))/32.d0
         sdelta = (-35.d0*dn**(3))/48.d0 + (105.d0*dn**(5))/256.d0
         sepsilon = 315.d0 * dn ** (4) / 512.d0
         slength = salpha * ( rlat + sbeta  * dsin(2.d0*rlat) + sgamma   * dsin(4.d0*rlat) &
                                   + sdelta * dsin(6.d0*rlat) + sepsilon * dsin(8.d0*rlat) )
!         zone = floor((dlon+180)/6) + 1
         cmeridian = ( -183.d0 + zone*6.d0 ) * pi / 180.d0

         sep2 = (a**(2) - b **(2)) / (b**(2))
         snu2 = sep2 * (dcos(rlat) ** (2))
         sN   = a*a / ( b*dsqrt(1.d0+snu2) )
         t    = dtan(rlat)
         t2   = t * t
         tmp  = ( t2*t2*t2 ) - t**(6)
         sl   = rlon - cmeridian
         sl3coef =    1.d0 -         t2                           +        snu2
         sl4coef =    5.d0 -         t2                           +   9.d0*snu2 +   4.d0*snu2*snu2
         sl5coef =    5.d0 -   18.d0*t2 +        t2*t2            +  14.d0*snu2 -  58.d0*  t2*snu2
         sl6coef =   61.d0 -   58.d0*t2 +        t2*t2            + 270.d0*snu2 - 330.d0*  t2*snu2
         sl7coef =   61.d0 -  479.d0*t2 + 179.d0*t2*t2 - t2*t2*t2
         sl8coef = 1385.d0 - 3311.d0*t2 + 543.d0*t2*t2 - t2*t2*t2
!
         x = sN * dcos(rlat)                * sl                &
           + sN * dcos(rlat)**(3) * sl3coef * sl**(3) /    6.d0 &
           + sN * dcos(rlat)**(5) * sl5coef * sl**(5) /  120.d0 &
           + sN * dcos(rlat)**(7) * sl7coef * sl**(7) / 5040.d0
         y = slength &
           + t * sN * dcos(rlat)**(2)           * sl**(2) /     2.d0 &
           + t * sN * dcos(rlat)**(4) * sl4coef * sl**(4) /    24.d0 &
           + t * sN * dcos(rlat)**(6) * sl6coef * sl**(6) /   720.d0 &
           + t * sN * dcos(rlat)**(8) * sl8coef * sl**(8) / 40320.d0
!
         x = x * UTMScaleFactor + 500000.d0
         y = y * UTMScaleFactor
         if( y < 0.0d0 ) then
            y = y + 10000000.d0
         endif
         xy(1,n) = x
         xy(2,n) = y
!         write(20+zone,*) x, y
      enddo
!
   end subroutine LatLonToUTM
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine showbar(ntotal, now, ncount)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   implicit none
   integer, intent(in) :: ntotal, now
   integer, intent(inout) :: ncount
   integer :: nout, n
!
   nout = int(dble(ntotal/50))
   n = mod(ntotal,50)
   if ( n /= 0 ) nout = nout + 1
!
   if( now >= ncount * nout ) then
      ncount = ncount + 1
      select case(ncount)
         case(10, 20, 30, 40, 50)
           write(6,'(a,$)') '+'
         case default
           write(6,'(a,$)') '-'
      end select
   endif
   end subroutine showbar
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine correct_lidar_using_GAP( imode )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata,      only: gridname, recordname
      use GAPdata!,       only: nGAPdata, GAPname
      implicit none
      integer, intent(in) :: imode
      integer :: i, istrings, igap_data
      character(len=2) :: yn
      character(len=10) :: cjunk
!
      write(6,*) '  Input Grid file name:'
      read(5,'(a)') gridname
      write(6,*) '  Input Node Property Record file name:'
      read(5,'(a)') recordname
      write(6,*) '  Input GAP/NLCD data file name:'
      read(5,'(a)') GAPname
!
      write(6,*) '  Select Data type (1:Land use, 2:Bathymetrty)'
      do
        read(5,*) igap_data
        select case(igap_data)
          case(1)
            write(6,*) '  Input Classified value table file name:'
            read(5,'(a)') GAPtable
            exit
          case(2)
            exit
          case default
            write(6,*) ' You must input 1 or 2.'
        end select
      enddo      
      
!
!
      write(6,*) ' Do you want converting Ascii GAP data to Binary(required):(Y/N)'
      do
         read(5,*) yn
         if( (yn == 'N') .or. (yn == 'n') ) then
            open(50,file=GAPname(1:len_trim(GAPname)),status='old',action='read')
              read(50,*) cjunk, ncol
              read(50,*) cjunk, nrow
              read(50,*) cjunk, xllGAP
              read(50,*) cjunk, yllGAP
              read(50,*) cjunk, cellsize
              read(50,*) cjunk, idef_val
            close(50)
            exit
         elseif( (yn == 'Y') .or. (yn == 'y') ) then
               call outGAP_Binary
               exit
         else
               write(6,*) ' You must input Y or N.; (Y/N)'
         endif
      enddo
!
  if( igap_data == 1 ) then
      call readctable
  endif
!
      call read14(imode)
      call readnprecord
      call mapping_CAP(imode,igap_data)
      cjunk = gridname(len_trim(gridname)-2:len_trim(gridname))
      if( (cjunk == "grd") .or. (cjunk == "GRD") ) then
         istrings = 3
      else if (cjunk == ".14") then
         istrings = 2
      else
         istrings = 0
      endif
      call outnew14(istrings,imode)
!
      cjunk = recordname(len_trim(recordname)-3:len_trim(recordname))
      if( (cjunk == ".rec") .or. (cjunk == ".REC") ) then
         istrings = 3
      else
         istrings = 0
      endif
      call outnprecord(istrings,imode)
!
!
   end subroutine correct_lidar_using_GAP
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine mapping_CAP(imode,igap_data)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use parameters
      use griddata
      use GAPdata
      use section
      implicit none
!
      integer, intent(in) :: imode, igap_data
!
      double precision,parameter :: eps=1.0d0
      double precision, parameter :: ft=0.3048 ![m]
      
!
      integer :: i, j, k, ib, n, m, ne, nv, nv2, length
      integer :: nout
      integer :: istart, iend, jstart, jend
      integer :: icmax, icmin, negaposi, nunit
      integer,allocatable :: GAPARRAY(:,:)
      double precision :: xl, xr, yl, yu, times
      double precision :: xmin,  xmax,  ymin,  ymax, ddx, ddy
      double precision :: x, y, value, ratio
      character(len=20) :: c
!
      integer, allocatable :: ncount(:)
!
      if(igap_data /= 1) iclass = 1
      allocate( ncount(iclass) )
!
! Moddify nflag
  if( igap_data == 1 ) then
      do n = 1, nnode
         if( (nflag(n)==2) .or. (nflag(n)==3) ) nflag(n)=1
         if( nprec(n) /= 1 ) cycle      ! IF Bathy data came from LIDAR data
         if( bathy(n) >= -0.8d0 ) then 
            select case(nmrec(n))
               case(1,2,3)
                  nflag(n) = 1
                  iscale(n) = 1
               case(4)
                  nflag(n) = 4
                  iscale(n) = 2
               case(5)
                  nflag(n) = 4
                  iscale(n) = 4
               case(7)
                  nflag(n) = 4
                  iscale(n) = 8
               case default
                  write(6,*) '       Node Property Record has wrong number'
                  write(6,*) '       System will stop.'
                  stop
            end select
         endif
      enddo
   else ! USE GAP FORMAT BATHYDATA
   

!...Added ZC   
        write(6,*) '  Input paremeter to convert for GRID '
        write(6,*) '       Nega-Posi: (if you want to convert, please input -1)'
        read(5,*) negaposi
        write(6,*)
        write(6,*) '       Do you want to convert the unit of database value?'
        write(6,*) '          0. No Change'
        write(6,*) '          1. Meter to Feet'
        write(6,*) '          2. Feet to Meter'
        read(5,*) nunit
        !
        select case (nunit)
         case(0)
            times = dble(negaposi)
         case(1)
            times = dble(negaposi) / ft
         case(2)
            times = dble(negaposi) * ft
         case default
            times = dble(negaposi)
        end select
!...

      do n = 1, nnode
         if( (nflag(n)==2) .or. (nflag(n)==3) ) nflag(n)=1
         if( nprec(n) /= 1 ) cycle      ! IF Bathy data came from LIDAR data
            select case(nmrec(n))
               case(1,2,3)
                  nflag(n) = 1
                  iscale(n) = 1
               case(4)
                  nflag(n) = 4
                  iscale(n) = 2
               case(5)
                  nflag(n) = 4
                  iscale(n) = 4
               case(7)
                  nflag(n) = 4
                  iscale(n) = 8
               case default
                  write(6,*) '       Node Property Record has wrong number'
                  write(6,*) '       System will stop.'
                  stop
            end select
      enddo
   endif
!
! Open Binary GAP data
      inquire( iolength = length ) i
      write(6,*) length
      open(51,file=GAPname(1:len_trim(GAPname))//'.binary',access='direct',recl=length)
#ifdef HIGHMEM
      !...Added ZC - On high memory machines, read entire dataset in at once for faster
      !   access
      WRITE(6,'(A,$)') "Now reading in full GIS database..."
      ALLOCATE(GAPARRAY(1:NROW,1:NCOL))
      DO I = 1,NROW
        DO J = 1,NCOL
            READ(51,REC=((I-1)*NCOL+J)) GAPARRAY(I,J)
        ENDDO
      ENDDO
      WRITE(6,'(A)') "done!"
#endif      
!
      xl = xllGAP
      xr = xllGAP + (ncol-1) * cellsize
      yl = yllGAP
      yu = yllGAP + (nrow-1) * cellsize
      write(6,*) xl, yl
      write(6,*) xr, yu
!
  if( igap_data == 1 ) then
      icmax=maxval(nclass(:))
      icmin=minval(nclass(:))
  endif
!
! MAPPING LOOP
      write(6,'(a)') '    Mapping to Grid Node'
      nout = 0
      Node_loop: do n = 1, nnode
         call showbar(nnode, n, nout)
         if(nflag(n)==0) cycle
         if((xy(1,n)<xl).or.(xy(1,n)>xr).or.(xy(2,n)<yl).or.(xy(2,n)>yu)) cycle
   ! Define grid size
         xmin = xy(1,n); xmax = xy(1,n)
         ymin = xy(2,n); ymax = xy(2,n)
         do ne = 1, iean(n)
            m = nean(n,ne)
            x = 0.0d0; y = 0.0d0
            do k = 1, 3
               x = x + xy(1,nc(k,m))
               y = y + xy(2,nc(k,m))
            enddo
               x = x / 3.0d0; y = y / 3.0d0
               xmin = dmin1(xmin,x)
               xmax = dmax1(xmax,x)
               ymin = dmin1(ymin,y)
               ymax = dmax1(ymax,y)
         enddo
!           nflag(n)==4 is Averaging in Twice Grid scale
         if( nflag(n) == 4 ) then
             ddx = (xmax - xmin) * 0.5d0
             ddy = (ymax - ymin) * 0.5d0
             xmin = xmin - ddx * dble(iscale(n)-1)
             xmax = xmax + ddx * dble(iscale(n)-1)
             ymin = ymin - ddy * dble(iscale(n)-1)
             ymax = ymax + ddy * dble(iscale(n)-1)
         endif
         if((xmin<xl).or.(xmax>xr).or.(ymin<yl).or.(ymax>yu)) cycle
!
             istart = nint( ( xmin - xllGAP ) / cellsize ) + 1
             jstart = nint( ( yu   - ymax   ) / cellsize ) + 1
             iend   = nint( ( xmax - xllGAP ) / cellsize ) + 1
             jend   = nint( ( yu   - ymin   ) / cellsize ) + 1
!
! Count
  if( igap_data == 1 ) then
         ncount(:) = 0
         do j = jstart, jend
            do i = istart, iend
               ib = (j-1) * ncol + i
               read(51,rec=ib) nv
               if( (nv == idef_val) ) cycle
               if( (nv < icmin) .or. (nv > icmax) ) cycle
               if( nclassi(nv) == idef_val ) cycle
               ncount(nclassi(nv)) = ncount(nclassi(nv)) + 1
            enddo
         enddo
  else
         ncount(1) = 0
         value = 0.0d0
         do j = jstart, jend
            do i = istart, iend
               ib = (j-1) * ncol + i
               read(51,rec=ib) nv
               if( (nv == idef_val) ) cycle
               ncount(1) = ncount(1) + 1
               value = value + dble(nv) * times / gap_multiply_factor
            enddo
         enddo
  endif
!#ifdef class
!         if( sum(ncount(:)) == 0 ) then
!           write(99,*)
!           write(99,*) 'node:',n
!           do j = jstart, jend
!              do i = istart, iend
!                 ib = (j-1) * ncol + i
!                 read(51,rec=ib) nv
!                 write(99,'(i5,$)') nv
!              enddo
!           enddo
!         endif
!#endif
         if( sum(ncount(:)) == 0 ) cycle
! nearest point
         i = nint( ( xy(1,n) - xllGAP ) / cellsize ) + 1
         j = nint( ( yu      - xy(2,n)) / cellsize ) + 1
         ib = (j-1) * ncol + i
#ifdef HIGHMEM
         nv = GAPARRAY(j,i)
         !read(51,rec=ib) nv2
         !if(nv.NE.nv2)then
         !   WRITE(6,*) "UT OH!"
         !   WRITE(6,*) nv,nv2
         !   STOP
         !endif
#else
         read(51,rec=ib) nv
#endif
  if( igap_data == 1 ) then
         if( nv == nclass(1) ) then  !nclass(1) is Water pixcel
            ratio = dble( ncount(nclassi(nclass(1))) ) / dble( sum(ncount(:)) )
            if( ratio >= 0.99d0 ) then
               bathy(n) = 1.2d0
!               bathy(n) = 0.4d0
               nprec(n) = imode
               nmrec(n) = 3
               cycle
            else if( ratio >= 0.90d0 ) then
               bathy(n) = 1.0d0
!               bathy(n) = 0.3d0
               nprec(n) = imode
               nmrec(n) = 3
               cycle
            else if( ratio >= 0.80d0 ) then
               bathy(n) = 0.8d0
!               bathy(n) = 0.2d0
               nprec(n) = imode
               nmrec(n) = 3
               cycle
            else if( ratio >= 0.70d0 ) then
               bathy(n) = 0.6d0
!               bathy(n) = 0.1d0
               nprec(n) = imode
               nmrec(n) = 3
               cycle
            else if( ratio >= 0.60d0 ) then
               bathy(n) = 0.4d0
!               bathy(n) = 0.1d0
               nprec(n) = imode
               nmrec(n) = 3
               cycle
            endif
         endif
         value = 0.0d0
         do k = 1, iclass
            value = value + vclass(k) * ncount(k)
         enddo
  endif
         bathy(n) = value / dble(sum(ncount(:)))
         nprec(n) = imode
         nmrec(n) = 1
         if ( nflag(n) == 4 ) nmrec(n) = int(iscale(n)/2) + 3
      enddo Node_loop
      write(6,*) 
      close(51)
!
   end subroutine mapping_CAP
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine outGAP_Binary
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use GAPdata
      implicit none
      integer :: length
      integer, allocatable :: icolval(:)
      character(len=80) :: cjunk
      integer :: i, j, n, icount, nout
!
      open(50,file=GAPname(1:len_trim(GAPname)),status='old',action='read')
      read(50,*) cjunk, ncol
      read(50,*) cjunk, nrow
      read(50,*) cjunk, xllGAP
      read(50,*) cjunk, yllGAP
      read(50,*) cjunk, cellsize
      read(50,*) cjunk, idef_val
!
      inquire( iolength = length ) i
      write(6,*) length
      open(51,file=GAPname(1:len_trim(GAPname))//'.binary',access='direct',recl=length)
      icount = 0
!
      allocate( icolval(ncol) )
!
      nout = 0
!
      write(6,'(a)')  GAPname(1:len_trim(GAPname))//'.binary'
      do i = 1, nrow
         read(50,*) ( icolval(j), j=1,ncol )
         do j = 1, ncol
            icount = icount + 1
            write(51,rec=icount) icolval(j)
         enddo
         call showbar(nrow, i, nout)
      enddo
      write(6,*)
      close(50)
      close(51)
      deallocate( icolval )
!
   end subroutine outGAP_Binary
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine GAP_map( imode )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata,      only: gridname
      use GAPdata
      implicit none
      integer, intent(in) :: imode
      integer :: i, j, istrings
      character(len=2) :: yn
      character(len=10) :: cjunk
      integer :: igap_data=1
!
      do 
        write(6,*) ' Do you want to map the data to:'
        write(6,*) '  1. One value on gdid node.(such as Mannings n)'
        write(6,*) '  2. Twelve values on gdid node.'
        write(6,*) '       (such as roughness at wind direction)'
        read(5,*) igap
        select case(igap)
          case(1,2) ! Lattice TYPE Database
           exit
          case default
            write(6,*) ' You MUST slect 1 or 2'
        end select
      enddo
!
    

      write(6,*) '  Input Grid file name:'
      read(5,'(a)') gridname
      write(6,*) '  Input GAP/NLCD data file name:'
      read(5,'(a)') GAPname
      write(6,*) '  Input Classified value table file name:'
      read(5,'(a)') GAPtable
!
!
      write(6,*) ' Do you want converting Ascii GAP data to Binary(required):(Y/N)'
      do
         read(5,*) yn
         if( (yn == 'N') .or. (yn == 'n') ) then
            open(50,file=GAPname(1:len_trim(GAPname)),status='old',action='read')
              read(50,*) cjunk, ncol
              read(50,*) cjunk, nrow
              read(50,*) cjunk, xllGAP
              read(50,*) cjunk, yllGAP
              read(50,*) cjunk, cellsize
              read(50,*) cjunk, idef_val
            close(50)
            exit
         elseif( (yn == 'Y') .or. (yn == 'y') ) then
               call outGAP_Binary
               exit
         else
               write(6,*) ' You must input Y or N.; (Y/N)'
         endif
      enddo
      call readctable
!
      if( igap == 1 ) j=imode
      if( igap == 2 ) j=imode*100
      call read14(j)
      call mapping_GAP
!OUTPUT
      cjunk = gridname(len_trim(gridname)-2:len_trim(gridname))
      if( (cjunk == "grd") .or. (cjunk == "GRD") ) then
         istrings = 3
      else if (cjunk == ".14") then
         istrings = 2
      else
         istrings = 0
      endif
      if( igap == 1 ) then
        call outnew14(istrings,imode)
      else if( igap ==2 ) then
        do i = 1, 12
           j = imode*100+i
           write(6,*) i, j
           call windin(i)
           call outnew14(istrings,j)
        enddo
      endif
!
   end subroutine GAP_map
!
 
   subroutine windin(i)
      use griddata, only:nnode, bathy
      use GAPdata,  only:wind12
      implicit none
      integer, intent(in) :: i
      integer :: n
      do n = 1, nnode
        bathy(n) = wind12(i,n)
      enddo
   end subroutine windin
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine mapping_GAP
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use parameters
      use griddata
      use GAPdata
      use section
!$    use omp_lib
      implicit none
!
      double precision,parameter :: eps =1.0d-6
!
      integer :: i, j, k, ib, n, m, ne, nv, nv2, length
      integer :: nout
      integer :: istart, iend, jstart, jend
      integer :: icmax, icmin, donenodes
      integer,allocatable :: GAPARRAY(:,:)
      double precision :: xl, xr, yl, yu
      double precision :: xmin,  xmax,  ymin,  ymax, ddx, ddy
      double precision :: x, y, value
      character(len=20) :: c
      integer :: istboard(-1:1,-3:3), nd
      double precision :: weight(0:12), tan_xy, dist, w, pi
      
!
      pi = acos(-1.0d0)
!
! Open Binary GAP data
      inquire( iolength = length ) i
      write(6,*) length
      open(51,file=GAPname(1:len_trim(GAPname))//'.binary',access='direct',recl=length)
!
      xl = xllGAP
      xr = xllGAP + (ncol-1) * cellsize
      yl = yllGAP
      yu = yllGAP + (nrow-1) * cellsize
      write(6,*) xl, yl
      write(6,*) xr, yu
#ifdef HIGHMEM
      !...Added ZC - On high memory machines, read entire dataset in at once for faster
      !   access
      WRITE(6,'(A,$)') "Now reading in full GIS database..."
      ALLOCATE(GAPARRAY(1:NROW,1:NCOL))
      DO I = 1,NROW
        DO J = 1,NCOL
            READ(51,REC=((I-1)*NCOL+J)) GAPARRAY(I,J)
        ENDDO
      ENDDO
      WRITE(6,'(A)') "done!"
#endif   
      
!
      icmax=maxval(nclass(:))
      icmin=minval(nclass(:))
!
! MAPPING LOOP

#ifdef HIGHMEM
!$    IF(OMP_GET_MAX_THREADS().GT.1)THEN
!$      write(6,'(a,i0,a)') '    Mapping to Grid Node using ',OMP_GET_MAX_THREADS(),' cores...'
!$    ELSE
        write(6,'(a)') '    Mapping to Grid Node'
!$    ENDIF
#else   
        write(6,'(a)') '    Mapping to Grid Node'
#endif     
      nout = 0
   if( igap == 1 ) then  ! One value on grid node.
      Node_loop: do n = 1, nnode
         call showbar(nnode, n, nout)
         if(nflag(n)==0) cycle
         if((xy(1,n)<xl).or.(xy(1,n)>xr).or.(xy(2,n)<yl).or.(xy(2,n)>yu)) cycle
   ! Define grid size
         xmin = xy(1,n); xmax = xy(1,n)
         ymin = xy(2,n); ymax = xy(2,n)
         do ne = 1, iean(n)
            m = nean(n,ne)
            x = 0.0d0; y = 0.0d0
            do k = 1, 3
               x = x + xy(1,nc(k,m))
               y = y + xy(2,nc(k,m))
            enddo
               x = x / 3.0d0; y = y / 3.0d0
               xmin = dmin1(xmin,x)
               xmax = dmax1(xmax,x)
               ymin = dmin1(ymin,y)
               ymax = dmax1(ymax,y)
         enddo
!           nflag(n)==4 is Averaging in Twice Grid scale
         if( nflag(n) == 4 ) then
             ddx = (xmax - xmin) * 0.5d0
             ddy = (ymax - ymin) * 0.5d0
             xmin = xmin - ddx * dble(iscale(n)-1)
             xmax = xmax + ddx * dble(iscale(n)-1)
             ymin = ymin - ddy * dble(iscale(n)-1)
             ymax = ymax + ddy * dble(iscale(n)-1)
         endif
         if((xmin<xl).or.(xmax>xr).or.(ymin<yl).or.(ymax>yu)) cycle
!
             istart = nint( ( xmin - xllGAP ) / cellsize ) + 1
             jstart = nint( ( yu   - ymax   ) / cellsize ) + 1
             iend   = nint( ( xmax - xllGAP ) / cellsize ) + 1
             jend   = nint( ( yu   - ymin   ) / cellsize ) + 1
!
             k = 0
             value = 0.0d0
! Average
         if ( (nflag(n)==1) .or. (nflag(n)==4) ) then
             do j = jstart, jend
                do i = istart, iend
#ifdef HIGHMEM
                   nv = GAPARRAY(j,i)
#else
                   ib = (j-1) * ncol + i
                   read(51,rec=ib) nv
#endif
                   if( (nv == idef_val) ) cycle
                   if( (nv < icmin) .or. (nv > icmax) ) cycle
                   if( nclassi(nv) == idef_val ) cycle
                   k = k + 1
                   value = value + vclass(nclassi(nv))
                enddo
             enddo
! Highest
         else if ( nflag(n) == 2 ) then
             do j = jstart, jend
                do i = istart, iend
#ifdef HIGHMEM
                   nv = GAPARRAY(j,i)
#else
                   ib = (j-1) * ncol + i
                   read(51,rec=ib) nv
#endif
                   if( (nv == idef_val) ) cycle
                   if( (nv < icmin) .or. (nv > icmax) ) cycle
                   if( nclassi(nv) == idef_val ) cycle
                   if( dabs(vclass(nclassi(nv))) > dabs(value) ) then
                      k = 1
                      value = vclass(nclassi(nv))
                   endif
                enddo
             enddo
! Nearest
         else if ( nflag(n) == 3 ) then
             i = nint( ( xy(1,n) - xllGAP ) / cellsize ) + 1
             j = nint( ( yu      - xy(2,n)) / cellsize ) + 1             
#ifdef HIGHMEM
             nv = GAPARRAY(j,i)
#else
             ib = (j-1) * ncol + i
             read(51,rec=ib) nv
#endif
             if( (nv == idef_val) ) cycle
             if( (nv < icmin) .or. (nv > icmax) ) cycle
             if( nclassi(nv) == idef_val ) cycle
             k = 1
             value = vclass(nclassi(nv))
         endif
         if( k /= 0 ) then
             nflag(n) = 0
             bathy(n) = value / dble(k)
         endif
      enddo Node_loop
      write(6,*) 
   else if( igap == 2 ) then ! 12 values on grid node
      call make_stboard( istboard )
      allocate( wind12(0:12,1:nnode) )
      wind12(0:12,1:nnode) = 0.0d0
      donenodes = 0
!
#ifndef ebug

#ifdef HIGHMEM
     !$OMP PARALLEL DEFAULT(SHARED) &
     !$OMP          PRIVATE(I,J,X,Y,NV,W,K,TAN_XY,WEIGHT,&
     !$OMP                  XMAX,XMIN,YMAX,YMIN,istart,iend,&
     !$OMP                  jstart,jend,dist)
     !$OMP DO SCHEDULE(DYNAMIC)
#endif
      Node_loop12: do n = 1, nnode 
#else
      write(6,*) 'Debug mode!!!!!!!!!!!!!!!!!'
      Node_loop12: do n = 855403, 855403
#endif
         !write(6,*) n
         !$OMP CRITICAL
         donenodes = donenodes + 1
         call showbar(nnode, donenodes, nout)
         !$OMP END CRITICAL
         if(nflag(n)==0) cycle
         if((xy(1,n)<xl).or.(xy(1,n)>xr).or.(xy(2,n)<yl).or.(xy(2,n)>yu)) cycle
      ! Define grid size
         xmin = xy(1,n)-wind_radius * 1000.d0
         xmax = xy(1,n)+wind_radius * 1000.d0
         ymin = xy(2,n)-wind_radius * 1000.d0
         ymax = xy(2,n)+wind_radius * 1000.d0
         if((xmin<xl).or.(xmax>xr).or.(ymin<yl).or.(ymax>yu)) cycle
!
         istart = nint( ( xmin - xllGAP ) / cellsize ) + 1
         jstart = nint( ( yu   - ymax   ) / cellsize ) + 1
         iend   = nint( ( xmax - xllGAP ) / cellsize ) + 1
         jend   = nint( ( yu   - ymin   ) / cellsize ) + 1
!
         weight(0:12) = 0.0d0         
         do j = jstart, jend
           do i = istart, iend
             x = ( dble(i)*cellsize + xllGAP - xy(1,n) ) / 1000.0d0
             y = (-dble(j)*cellsize + yu     - xy(2,n) ) / 1000.0d0
             dist = x*x+y*y
             if( dsqrt(dist) > wind_radius ) cycle
#ifdef HIGHMEM
             nv = GAPARRAY(j,i)
#else
             ib = (j-1) * ncol + i
             read(51,rec=ib) nv
#endif
             if( (nv == idef_val) ) cycle
             if( (nv < icmin) .or. (nv > icmax) ) cycle
             if( nclassi(nv) == idef_val ) cycle
               w = 0.5d0 * dist / (wind_sigma*wind_sigma)
               w = exp(w) * ((2.0d0*pi*wind_sigma)**(1d0/2d0))
               w = 1.0d0 / w
               !write(6,*) w, nv, nclassi(nv), vclass(nclassi(nv))
               if( (dist**(1d0/2d0)) <= eps ) then
                  weight(0) = weight(0) + w
                  wind12(0,n) = wind12(0,n) + w * vclass(nclassi(nv))
                  cycle
               endif
               if( dabs(x) <= eps ) then
                  tan_xy = 10000000.0d0
               else
                  tan_xy = dabs(y/x)
               endif

               k =     min(1,int(tan_xy/(2-dsqrt(3.0d0))))
               k = k + min(1,int(tan_xy                 ))
               k = k + min(1,int(tan_xy/(2+dsqrt(3.0d0))))
               if( abs(k) > 3 ) then
                 write(6,*) 'K was overflowed!', n
                 write(6,*) j, i, k, tan_xy, x, y, w
                 stop
               endif
               nd = istboard(nint(dsign(1.0d0,x)),k*nint(dsign(1.0d0,y)))
!               write(6,*) i,j,nd
               weight(nd) = weight(nd) + w
               wind12(nd,n) = wind12(nd,n) + w * vclass(nclassi(nv))
           enddo
         enddo
         do i = 1, 12
           w = weight(i) + weight(0)
#ifdef ebug
           write(6,*) i, w, wind12(i,n), wind12(i,n)/w
#endif
           if( w <= 1.0d-12 ) cycle
           wind12(i,n) = wind12(i,n) / w
         enddo
      enddo Node_loop12
#ifdef HIGHMEM      
      !$OMP END DO
      !$OMP END PARALLEL
#endif
      write(6,*) 
   endif
      close(51)
!
   end subroutine mapping_GAP
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine make_stboard( istboard )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      implicit none
      integer, intent(out) :: istboard(-1:1,-3:3)
      !Direction is Direction vector of wind velocity
      ! So, we shoud pick up the upstream values!
      istboard( 1, 0) =  7
      istboard( 1, 1) =  8
      istboard( 1, 2) =  9
      istboard( 1, 3) = 10
      istboard( 0, 3) = 10
      istboard(-1, 3) = 10
      istboard(-1, 2) = 11 
      istboard(-1, 1) = 12
      istboard(-1, 0) =  1
      istboard(-1,-1) =  2
      istboard(-1,-2) =  3
      istboard(-1,-3) =  4
      istboard( 0,-3) =  4
      istboard( 1,-3) =  4
      istboard( 1,-2) =  5
      istboard( 1,-1) =  6
      istboard( 0, 2) =  0
      istboard( 0, 1) =  0
      istboard( 0, 0) =  0
      istboard( 0,-1) =  0
      istboard( 0,-2) =  0
   end subroutine make_stboard
!
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine readctable
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use parameters, only: defval
      use GAPdata, only: GAPtable, iclass, nclass, vclass, nclassi, idef_val
      implicit none
!
      integer :: i, imax, imin
      double precision,parameter :: eps=1.0d0
!
      open(12,file=GAPtable,status='old',action='read')
      read(12,*) iclass
      allocate( nclass(iclass), vclass(iclass) )
      do i = 1, iclass
         read(12,*) nclass(i), vclass(i)
      enddo
      imax = maxval(nclass(:),idef_val)
      imin = minval(nclass(:),idef_val)
!
      allocate( nclassi(imin:imax) )
      nclassi(:) = idef_val
      do i = 1, iclass
         nclassi(nclass(i)) = i
         if( dabs(vclass(i)-defval) <= eps ) then
            nclassi(nclass(i)) = idef_val ! Ignore this class
         endif
      enddo
!
!
   end subroutine readctable
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine smoothing( imode )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata,      only: gridname
      implicit none
      integer, intent(in) :: imode
      integer :: i, istrings
      character(len=10) :: cjunk
!
      write(6,*) '   Input GRID NAME:'
      read(5,'(a)') gridname
!
      call read14(imode)
      call smooth_LS
!
      cjunk = gridname(len_trim(gridname)-2:len_trim(gridname))
      if( (cjunk == "grd") .or. (cjunk == "GRD") ) then
         istrings = 3
      else if (cjunk == ".14") then
         istrings = 2
      else
         istrings = 0
      endif
      call outnew14(istrings,imode)
!
   end subroutine smoothing
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine smooth_LS
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata
      implicit none
      character(len=120) :: cjunk
      integer ::nsm
      integer, allocatable :: nlist(:)
      double precision, allocatable ::  area(:), temp(:)
      integer :: i, in, n, je, m, smooth_it, it,junki
      double precision :: aall, wv, eave,junkr,flagval
      logical, allocatable :: flagnode(:)
!
      allocate( area(nelem) )
      write(6,*) '   Input Smoothing template file (grid/flag list):'
      read(5,'(a)') cjunk
      write(6,*) '   Number of Smoothing Iterations: '
      read(5,*) smooth_it
      open(30,file=cjunk,status='old',action='read')
      write(6,*) '    Select node list format.'
      write(6,*) '      1. Node number list'
      write(6,*) '      2. Flagged ADCIRC Grid'
      read(5,*) je
      if( je == 1 ) then
         read(30,*)
         read(30,*) nsm
         allocate( nlist(nsm), temp(nsm) )
         do i = 1, nsm
           read(30,*) nlist(i)
         enddo
      endif
      if( je == 2 ) then
        read(30,*) cjunk
        read(30,*) junki,nsm
        allocate( flagnode(nsm) )
        flagnode(:) = .false.
        do i = 1,nsm
            read(30,*) junki,junkr,junkr,flagval
            if(flagval .le. -7777d0)then
                flagnode(i) = .true.
            endif
        enddo   
      endif
!
      call calarea( area )
!
      do it = 1,smooth_it
          if( je == 1 )then
              do in = 1, nsm
                 n = nlist(in)
                 wv = 0.0d0
                 aall = 0.0d0
                 do je = 1, iean(n)
                    m = nean(n,je)
                    eave = 0.d0
                    do i = 1, 3
                       eave = eave + bathy(nc(i,m))
                    enddo
                    wv = wv + eave * area(m) / 3.0d0
                    aall = aall + area(m)
                 enddo
                 temp(in) = wv / aall
              enddo
!
! Update Bathy
              do in = 1, nsm
                 bathy(nlist(in)) = temp(in)
              enddo
              
          elseif( je == 2 )then
              do in = 1, nsm
                 if( .NOT. flagnode(in) )cycle
                 n = in
                 wv = 0.0d0
                 aall = 0.0d0
                 do je = 1, iean(n)
                    m = nean(n,je)
                    eave = 0.d0
                    do i = 1, 3
                       eave = eave + bathy(nc(i,m))
                    enddo
                    wv = wv + eave * area(m) / 3.0d0
                    aall = aall + area(m)
                 enddo
                 bathy(in) = wv / aall
              enddo      
          endif

      enddo
!

   end subroutine smooth_LS
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine calarea( area )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata
      implicit none
      double precision, intent(out) :: area(nelem)
      integer :: m, n1, n2, n3
      double precision :: x1, x2, x3, y1, y2, y3, a02
!
      do m = 1, nelem
         n1 = nc(1,m)
         n2 = nc(2,m)
         n3 = nc(3,m)
         x1 = xy(1,n1)
         x2 = xy(1,n2)
         x3 = xy(1,n3)
         y1 = xy(2,n1)
         y2 = xy(2,n2)
         y3 = xy(2,n3)
         a02 = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
         if ( a02 <= 0.d0 ) then
            write(6,*) '003: Area Failure',m
         endif
         area(m) = a02 * 0.5d0
      enddo
!
   end subroutine calarea
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
!
!
!
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine unstructure()
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      implicit none
      integer :: imode
!
      do
        write(6,*)
        write(6,*) ' Select mode'
        write(6,*) '   1. Bathy. Mapping'
!
        read(5,*) imode
!
        select case (imode)
          case(1)
            imode = imode + 6
            call ubathy_map( imode )
            exit
          case default
        end select
      enddo

   end subroutine unstructure
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine ubathy_map( imode )
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata,   only: gridname, recordname
      implicit none
      integer, intent(in) :: imode
      integer :: i, istrings
      double precision :: dmemory
      character(len=10) :: cjunk, yn
      character(len=100) :: ugisname
!
      write(6,*) '  Input Grid file name:'
      read(5,'(a)') gridname
!      write(6,*) '  Input Node Property Record file name:'
!      read(5,'(a)') recordname
      write(6,*) '  Input Unstructure database file name:'
      read(5,'(a)') ugisname
!
      call read14(imode)
      call readnprecord
      call make_node_table
!
      call map_ugisdata(ugisname,imode) ! Reading unstructure GIS DATA & Mapping on GRID.
!
!
! Define the expansion of Gridfilename
      cjunk = gridname(len_trim(gridname)-2:len_trim(gridname))
      if( (cjunk == "grd") .or. (cjunk == "GRD") ) then
         istrings = 3
      else if (cjunk == ".14") then
         istrings = 2
      else
         istrings = 0
      endif
      call outnew14(istrings,imode)
!
!! Define the expansion of recordfile name
!      cjunk = recordname(len_trim(recordname)-3:len_trim(recordname))
!      if( (cjunk == ".rec") .or. (cjunk == ".REC") ) then
!         istrings = 3
!      else
!         istrings = 0
!      endif
!      call outnprecord(istrings,imode)

   end subroutine ubathy_map
!   
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine map_ugisdata(ugisname,imode)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata, only:nnode
      use gridtable, only:idiv, dx
      implicit none
      character(len=100), intent(in) :: ugisname
      integer, intent(in) :: imode
      integer :: npgis, negaposi, nunit
!
      double precision, parameter :: ft=0.3048 ![m]
!
      double precision :: xg, yg, vg, times, rr
      integer :: np, nout
      integer, allocatable:: ncount(:)
      double precision, allocatable :: value(:), rmin(:)
!
      integer :: nouti, istatus, nouto
!
      allocate( ncount(1:nnode), value(1:nnode),rmin(1:nnode) )
!
      write(6,*) '  Input paremeter to convert for GRID '
      write(6,*) '       Nega-Posi: (if you want to convert, please input -1)'
      read(5,*) negaposi
      write(6,*)
      write(6,*) '       Do you want to convert the unit of database value?'
      write(6,*) '          0. No Change'
      write(6,*) '          1. Meter to Feet'
      write(6,*) '          2. Feet to Meter'
      read(5,*) nunit
!
      select case (nunit)
         case(0)
            times = dble(negaposi)
         case(1)
            times = dble(negaposi) / ft
         case(2)
            times = dble(negaposi) * ft
         case default
            times = dble(negaposi)
      end select
!
      open(11,file=ugisname,status='old',action='read')
!
      ncount(1:nnode) = 0
      value(1:nnode) = 0.0d0
      rr = dsqrt( ( dx(1)*idiv )**2 + ( dx(2)*idiv )**2 )
      rmin(1:nnode) = rr
!
      nout = 0
      nouti = 0
      nouto = 0
      do
        read(11,*,iostat=istatus) xg, yg, vg
        if( istatus < 0 ) exit
        vg = vg * times
        call map_ugis(xg,yg,vg,ncount,value,rmin)
!taizo
        nout = nout + 1
        if( nout == 10000 ) then
          nouti = nouti + 1
          select case(nouti)
             case(10,20,30,40)
               write(6,'(a,$)') '+'
             case(50)
               nouto = nouto + 1
               write(6,'(a,$)') '+'
               write(6,*) nouto
               nouti = 0
             case default
               write(6,'(a,$)') '-'
          end select
        nout = 0
        endif
      enddo
!
      write(6,*) 
      call update_bathy(ncount,value,imode)
!
   end subroutine map_ugisdata
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine map_ugis(xg,yg,vg,ncount,value,rmin)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata
      use gridtable
      implicit none
      double precision, intent(in) :: xg, yg, vg
      integer, intent(inout) :: ncount(nnode)
      double precision, intent(inout) :: value(nnode), rmin(nnode)
!
      integer :: i, j, ista, iend , jsta, jend, n, m, ni, ne, k
      double precision :: xmin, xmax, ymin, ymax, ddx, ddy, x, y
!
! Quick turn if the gis point is out of Grid area
      if(  (xg < xll(1)) .or. (yg < xll(2))  &
       .or.(xg > xll(1) + dx(1) * idiv )     &
       .or.(yg > xll(2) + dx(2) * idiv )     ) return
!
      i = int( (xg-xll(1))/dx(1) ) + 1
      j = int( (yg-xll(2))/dx(2) ) + 1
      ista = max(1,i-iover)
      iend = min(idiv,i+iover)
      jsta = max(1,j-iover)
      jend = min(idiv,j+iover)
!
      Block_i:do i = ista, iend
        Block_j:do j = jsta, jend
         ! Quick turn if the gis point is out of Grid area
          if( npiece(i,j) == 0 ) cycle
          if(  (xg < xypiece(1,2,i,j)) .or. (yg < xypiece(2,2,i,j))  &
           .or.(xg > xypiece(1,1,i,j)) .or. (yg > xypiece(2,1,i,j))  ) cycle
          Node_Block_ij:do ni = 1, npiece(i,j)
            n = npiece_list(npiece_add(i,j)+ni)
          ! Grid size
            xmin = xgs(1,n)
            ymin = xgs(2,n)
            xmax = xgs(3,n)
            ymax = xgs(4,n)

            if(  (xg < xmin) .or. (yg < ymin)  &
             .or.(xg > xmax) .or. (yg > ymax)  ) cycle
!
!        Average
            if( (nflag(n) == 1) .or. (nflag(n) == 4) ) then
                value(n) = value(n) + vg
                ncount(n) = ncount(n) + 1
!        Highest
            elseif( nflag(n) == 2 ) then
                value(n) = dmin1(value(n),vg)
                ncount(n) = 1
            elseif( nflag(n) == 3 ) then
                x = xy(1,n) - xg; y = xy(2,n) - yg
                x = dsqrt( x*x + y*y )
                if( x < rmin(n) ) then
                  value(n) = vg
                  ncount(n) = 1
                  rmin(n) = x
                endif
            endif
          enddo Node_Block_ij
        enddo Block_j
      enddo Block_i
!
   end subroutine map_ugis
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine update_bathy(ncount,value,imode)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata
      implicit none
      integer, intent(in) :: ncount(nnode), imode
      double precision, intent(in) :: value(nnode)
      integer :: n
!
      do n = 1, nnode
        if( ncount(n) == 0 ) cycle
!        if( times* value(n) <= 0.0d0 ) cycle
        bathy(n) = value(n) / dble(ncount(n))
        if( (nflag(n) == 1) .or. (nflag(n) == 4) ) then
          if( iscale(n) == 1 ) then
             nprec(n) = imode; nmrec(n) = 1
          elseif( iscale(n) == 2 ) then
             nprec(n) = imode; nmrec(n) = 4
          elseif( iscale(n) == 4 ) then
             nprec(n) = imode; nmrec(n) = 5
          elseif( iscale(n) == 8 ) then
             nprec(n) = imode; nmrec(n) = 7
          endif
        else 
          nprec(n) = imode
          nmrec(n) = nflag(n)
        endif
      enddo

   end subroutine update_bathy
!
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine make_node_table
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      use griddata
      use gridtable
      implicit none
!
      double precision :: xmin(2), xmax(2), x, y, ddx, ddy
      integer :: i, j, k, ni, n, ne, m, id
!
      allocate( npiece_add(idiv,idiv), npiece(idiv,idiv), npiece_list(nnode) )
      call count_list(nnode, xy, nflag, xmax, xmin, dx, idiv,npiece_add, npiece, npiece_list)
      xll(1:2) = xmin(1:2)
      allocate( xypiece(2,2,idiv,idiv), xgs(4,nnode) )
      xypiece(1,1:2,1:idiv,1:idiv) = xy(1,1)
      xypiece(2,1:2,1:idiv,1:idiv) = xy(2,1)
      gsmax = 0.0d0
      do i = 1, idiv
        do j = 1, idiv
          if( npiece(i,j) /= 0 ) then
            n = npiece_list(1+npiece_add(i,j))
            xypiece(1,1,i,j) = xy(1,n)
            xypiece(1,2,i,j) = xy(1,n)
            xypiece(2,1,i,j) = xy(2,n)
            xypiece(2,2,i,j) = xy(2,n)
          endif
          do ni = 1, npiece(i,j)
            n = npiece_list(ni + npiece_add(i,j))
            xmin(1) = xy(1,n); xmax(1) = xy(1,n)
            xmin(2) = xy(2,n); xmax(2) = xy(2,n)
               do ne = 1, iean(n)
                 m = nean(n,ne)
                 x = 0.0d0; y = 0.0d0
                 do k = 1, 3
                   x = x + xy(1,nc(k,m))
                   y = y + xy(2,nc(k,m))
                 enddo
                   x = x / 3.d0; y = y / 3.d0
                   xmin(1) = dmin1(xmin(1),x)
                   xmax(1) = dmax1(xmax(1),x)
                   xmin(2) = dmin1(xmin(2),y)
                   xmax(2) = dmax1(xmax(2),y)
               enddo
               ddx = (xmax(1) - xmin(1)) * 0.5d0
               ddy = (xmax(2) - xmin(2)) * 0.5d0
               if( nflag(n) == 4 ) then
                 ddx = ddx * dble(iscale(n)-1)
                 ddy = ddy * dble(iscale(n)-1)
                 xmin(1) = xmin(1) - ddx
                 xmax(1) = xmax(1) + ddx
                 xmin(2) = xmin(2) - ddy
                 xmax(2) = xmax(2) + ddy
               endif
            do id = 1, 2
              xypiece(id,1,i,j) = dmax1( xypiece(id,1,i,j), xmax(id) )
              xypiece(id,2,i,j) = dmin1( xypiece(id,2,i,j), xmin(id) )
            enddo
            gsmax = dmax1(gsmax,dabs(ddx),dabs(ddy))
            xgs(1,n) = xmin(1)
            xgs(2,n) = xmin(2)
            xgs(3,n) = xmax(1)
            xgs(4,n) = xmax(2)
          enddo
        enddo
      enddo
      iover = int(gsmax/maxval(dx(1:2))) + 1
      write(6,*) gsmax, dx(1), dx(2)
      write(6,*) '  *Check Overlap layer:',iover
!
   end subroutine make_node_table
!
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
   subroutine count_list(np, xyd, nflag, xmax, xmin, dx, idiv,npiece_add,npiece, npiece_list)
!-----+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
      implicit none
      integer,intent(in) :: np, idiv, nflag(np)
      double precision, intent(in) :: xyd(2,np)
!
      integer, intent(out) :: npiece(idiv,idiv), npiece_add(idiv,idiv)
      integer, intent(out) :: npiece_list(np)
      double precision, intent(out) :: xmax(2), xmin(2), dx(2)
!
      integer :: i, j, im , m, n, ix(2), istart
!
      do i = 1, 2
        xmin(i) = minval(xyd(i,1:np))
        xmax(i) = maxval(xyd(i,1:np))
      enddo
!
      write(6,*) xmin(1), xmin(2)
      write(6,*) xmax(1), xmax(2)
!
      do i = 1, 2
         xmax(i) = xmax(i) + 1.d0
      enddo
!
      dx(1:2) = ( xmax(1:2)-xmin(1:2) ) / idiv
      npiece(1:idiv,1:idiv) = 0
      do n = 1, np
        if( nflag(n) == 0 ) cycle
        do i = 1, 2
          ix(i) = int( (xyd(i,n)-xmin(i)) / dx(i) ) + 1
        enddo
        npiece(ix(1),ix(2)) = npiece(ix(1),ix(2)) + 1
      enddo
      
      istart = 0
      do i = 1, idiv
        do j = 1, idiv
          npiece_add(i,j) = istart
          istart = istart + npiece(i,j)
        enddo
      enddo
      write(6,*) sum( npiece(:,:) ), np
      npiece(1:idiv,1:idiv) = 0
      do n = 1, np
        if( nflag(n) == 0 ) cycle
        do i = 1, 2
          ix(i) = int( (xyd(i,n)-xmin(i)) / dx(i) ) + 1
        enddo
        npiece(ix(1),ix(2)) = npiece(ix(1),ix(2)) + 1
        npiece_list(npiece(ix(1),ix(2))+npiece_add(ix(1),ix(2))) = n
      enddo
      write(6,*) sum( npiece(:,:) ), np
   end subroutine count_list
!
